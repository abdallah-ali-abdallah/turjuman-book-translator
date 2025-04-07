import os
import json
import uuid
import time
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

import requests # Needed for handle_errors, though it's in exceptions.py now
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Ensure correct import paths if running as part of package 'src'
try:
    from .state import TranslationState, TerminologyEntry
    from .providers import get_llm_client
    from .chunking import create_semantic_chunks
    from .utils import log_to_state, update_progress
    from .exceptions import AuthenticationError, RateLimitError, APIError, handle_errors # Import exceptions and handler
    from .node_utils import safe_json_parse # Import utility
except ImportError: # Fallback for potential direct script execution (less ideal)
    from .state import TranslationState, TerminologyEntry
    from .providers import get_llm_client
    from .chunking import create_semantic_chunks
    from .utils import log_to_state, update_progress
    from .exceptions import AuthenticationError, RateLimitError, APIError, handle_errors
    from .node_utils import safe_json_parse


# --- Preprocessing Node Implementations ---

def init_translation(state: TranslationState) -> TranslationState:
    """Initializes state for a new translation job."""
    NODE_NAME = "init_translation"
    # Ensure state components are dictionaries if they exist, otherwise initialize
    state_dict = state if isinstance(state, dict) else {} # Work with dict internally
    state_dict['job_id'] = state_dict.get('job_id', f"job_{uuid.uuid4()}")
    state_dict['logs'] = state_dict.get('logs', [])
    state_dict['metrics'] = state_dict.get('metrics', {
        "start_time": time.time(),
        "end_time": None
    })
    # Initialize other fields expected later if they don't exist
    state_dict.setdefault('original_content', '')
    state_dict.setdefault('config', {})
    state_dict.setdefault('current_step', None)
    state_dict.setdefault('progress_percent', 0.0)
    state_dict.setdefault('chunks', None)
    state_dict.setdefault('terminology', None)
    state_dict.setdefault('translated_chunks', None)
    state_dict.setdefault('parallel_worker_results', None)
    state_dict.setdefault('critiques', []) # Explicitly initialize critiques list
    state_dict.setdefault('final_chunks', None) # Initialize final_chunks list
    state_dict.setdefault('final_document', None)
    state_dict.setdefault('error_info', None)

    update_progress(state_dict, NODE_NAME, 0.0)
    log_to_state(state_dict, f"Initialized job {state_dict['job_id']}", "INFO", node=NODE_NAME)
    # Ensure correct state type is returned (assuming TranslationState can be created from dict)
    # If TranslationState is a TypedDict or Pydantic model, this might need adjustment
    # For now, assuming it can handle dict unpacking or direct dict return is acceptable by LangGraph
    return state_dict # Return the dictionary



    return state


def chunk_document(state: TranslationState) -> TranslationState:
    NODE_NAME = "chunk_document"
    update_progress(state, NODE_NAME, 10.0)
    state["chunks"] = [] # Reset/initialize
    state["translated_chunks"] = [] # Also reset translated chunks array

    if not state.get('original_content'):
        log_to_state(state, "Original content is empty, cannot chunk.", "ERROR", node=NODE_NAME)
        state["error_info"] = "Cannot chunk empty content."
        return state

    try:
        content = state["original_content"]
        config = state.get("config", {})

        # --- Get Chunking Parameters from Environment ---
        # Max Chunk Size
        default_max_size = 2000
        try:
            max_size = int(os.environ.get("MAX_CHUNK_SIZE", default_max_size))
            if max_size <= 0:
                max_size = default_max_size
                log_to_state(state, f"Invalid MAX_CHUNK_SIZE env var <= 0, using default: {max_size}", "WARNING", node=NODE_NAME)
        except ValueError:
            max_size = default_max_size
            log_to_state(state, f"Non-integer MAX_CHUNK_SIZE env var, using default: {max_size}", "WARNING", node=NODE_NAME)

        # Min Chunk Size
        default_min_size = 100 # Example default minimum size
        try:
            min_size = int(os.environ.get("MIN_CHUNK_SIZE", default_min_size))
            if min_size < 0: # Allow 0, but not negative
                 min_size = default_min_size
                 log_to_state(state, f"Invalid MIN_CHUNK_SIZE env var < 0, using default: {min_size}", "WARNING", node=NODE_NAME)
            elif min_size > max_size:
                 min_size = max_size # Cannot be larger than max_size
                 log_to_state(state, f"MIN_CHUNK_SIZE env var > MAX_CHUNK_SIZE, setting min_size = max_size ({min_size})", "WARNING", node=NODE_NAME)
        except ValueError:
            min_size = default_min_size
            log_to_state(state, f"Non-integer MIN_CHUNK_SIZE env var, using default: {min_size}", "WARNING", node=NODE_NAME)

        # Detect if content has code blocks or images and adjust chunk size if needed
        has_code = "```" in content
        has_images = "![" in content

        if has_code or has_images:
            # Use smaller chunks for content with code or images
            suggested_size = min(max_size, 1200) # Example reduced size
            if max_size > suggested_size:
                log_to_state(state,
                    f"Content contains code blocks or images. Reducing chunk size from {max_size} to {suggested_size} for better handling.",
                    "INFO", node=NODE_NAME)
                max_size = suggested_size

        # Create chunks with the appropriate size
        initial_chunks = create_semantic_chunks(content, max_chunk_size=max_size)

        # --- Merge small chunks ---
        merged_chunks = []
        temp_chunk = ""
        for i, chunk in enumerate(initial_chunks):
            # Estimate length simply by character count for merging decision
            current_len = len(chunk)
            temp_len = len(temp_chunk)

            if temp_chunk and (temp_len + current_len) <= max_size:
                # If adding the current chunk doesn't exceed max_size, merge it
                temp_chunk += "\n\n" + chunk # Add separator
            elif current_len < min_size and i < len(initial_chunks) - 1:
                # If the current chunk is too small (and not the last one), start merging
                if temp_chunk: # Add previous temp_chunk if it exists
                    merged_chunks.append(temp_chunk)
                temp_chunk = chunk # Start a new temp_chunk with the small one
            else:
                # If the current chunk is large enough or merging would exceed max_size
                if temp_chunk: # Add the previous temp_chunk first
                    merged_chunks.append(temp_chunk)
                    temp_chunk = "" # Reset temp_chunk
                merged_chunks.append(chunk) # Add the current chunk

        # Add any remaining temp_chunk
        if temp_chunk:
            merged_chunks.append(temp_chunk)

        chunks = merged_chunks
        log_to_state(state, f"Initial chunks: {len(initial_chunks)}, After merging small chunks (<{min_size}): {len(chunks)}", "DEBUG", node=NODE_NAME)

        # Validate chunks to ensure code blocks aren't split (basic check)
        validated_chunks = []
        for chunk in chunks:
            # Count opening and closing code fences
            open_fences = chunk.count("```")
            # If odd number of fences, the chunk might have split a code block
            if open_fences % 2 != 0:
                log_to_state(state,
                    f"Detected potentially split code block in chunk (odd number of '```'). Review recommended.",
                    "WARNING", node=NODE_NAME)
                # More sophisticated validation could try to rejoin, but for now, just log.
            validated_chunks.append(chunk)

        state["chunks"] = validated_chunks
        # Initialize translated_chunks only if chunking succeeds
        state["translated_chunks"] = [None] * len(validated_chunks)
        log_to_state(state,
            f"Document split into {len(validated_chunks)} semantic chunks (max size ~{max_size}).",
            "INFO", node=NODE_NAME)
    except Exception as e:
        error_msg = f"Critical error during document chunking: {type(e).__name__}: {e}"
        log_to_state(state, error_msg, "CRITICAL", node=NODE_NAME)
        state["error_info"] = error_msg # Chunking failure is critical
        state["chunks"] = [] # Ensure chunks list is empty on failure
        state["translated_chunks"] = []

    return state


def terminology_unification(state: TranslationState) -> TranslationState:
    NODE_NAME = "terminology_unification"
    update_progress(state, NODE_NAME, 5.0)
    state["unified_terminology"] = []  # Initialize/reset

    if not state.get("original_content"):
        log_to_state(state, "Original content is empty, skipping terminology unification.", "WARNING", node=NODE_NAME)
        return state

    try:
        config = state.get("config", {})
        content = state["original_content"]

        # Read chunk size from environment
        default_chunk_size = 8000
        try:
            chunk_size = int(os.environ.get("TERMINOLOGY_EXTRACTION_CHUNK_SIZE", default_chunk_size))
            if chunk_size <= 0:
                chunk_size = default_chunk_size
        except ValueError:
            chunk_size = default_chunk_size

        # Read minimum chunk size
        default_min_size = 1000
        try:
            min_size = int(os.environ.get("TERMINOLOGY_MIN_CHUNK_SIZE", default_min_size))
            if min_size < 0:
                min_size = default_min_size
        except ValueError:
            min_size = default_min_size

        # Decide chunking strategy
        if len(content) <= min_size:
            chunks = [content]
            log_to_state(state, f"Content length <= {min_size}, treating as a single chunk for terminology extraction.", "INFO", node=NODE_NAME)
        else:
            initial_chunks = create_semantic_chunks(content, max_chunk_size=chunk_size)
            log_to_state(state, f"Initial terminology chunks before merging: {len(initial_chunks)}", "DEBUG", node=NODE_NAME)

            # Merge small chunks similar to chunk_document
            merged_chunks = []
            temp_chunk = ""
            for i, chunk in enumerate(initial_chunks):
                current_len = len(chunk)
                temp_len = len(temp_chunk)

                if temp_chunk and (temp_len + current_len) <= chunk_size:
                    temp_chunk += "\n\n" + chunk
                elif current_len < min_size and i < len(initial_chunks) - 1:
                    if temp_chunk:
                        merged_chunks.append(temp_chunk)
                    temp_chunk = chunk
                else:
                    if temp_chunk:
                        merged_chunks.append(temp_chunk)
                        temp_chunk = ""
                    merged_chunks.append(chunk)

            if temp_chunk:
                merged_chunks.append(temp_chunk)

            chunks = merged_chunks
            log_to_state(state, f"Terminology chunks after merging small chunks (<{min_size}): {len(chunks)}", "INFO", node=NODE_NAME)

        # Load prompts
        prompts_path = Path(__file__).parent.parent / "prompts.yaml"
        with open(prompts_path) as f:
            prompts = yaml.safe_load(f)

        prompt_text = prompts["prompts"]["unified_terminology_extraction"]["system"]

        llm = get_llm_client(config)

        all_terms = []
        seen_terms = set()

        for idx, chunk_text in enumerate(chunks):
            try:
                messages = [("system", prompt_text)]
                prompt_template = ChatPromptTemplate.from_messages(messages)
                chain = prompt_template | llm | StrOutputParser()

                response = chain.invoke({
                    "source_language": config.get("source_language", "english"),
                    "target_language": config.get("target_language", "arabic"),
                    "content_type": config.get("content_type", "general document"),
                    "chunk_content": chunk_text
                })

                log_to_state(state, f"Chunk {idx+1}/{len(chunks)} terminology response: {response}", "DEBUG", node=NODE_NAME)

                response_data = safe_json_parse(response, state, NODE_NAME)

                if isinstance(response_data, list):
                    for term_data in response_data:
                        if not isinstance(term_data, dict):
                            continue
                        source_term = term_data.get("sourceTerm")
                        if not isinstance(source_term, str) or not source_term.strip():
                            continue
                        if source_term in seen_terms:
                            continue  # Deduplicate, keep first occurrence
                        seen_terms.add(source_term)

                        # Validate proposedTranslations
                        translations = term_data.get("proposedTranslations", {})
                        if not isinstance(translations, dict) or "default" not in translations:
                            translations = {"default": ""}

                        entry = TerminologyEntry(
                            termId=f"term_{uuid.uuid4()}",
                            sourceTerm=source_term,
                            context=term_data.get("context", ""),
                            proposedTranslations=translations,
                            status="pending",
                            approvedTranslation=None,
                            variants=term_data.get("variants", [])
                        )

                        # Ensure variants is a list of strings
                        if not isinstance(entry["variants"], list) or not all(isinstance(v, str) for v in entry["variants"]):
                            entry["variants"] = []

                        all_terms.append(entry)

            except Exception as e:
                log_to_state(state, f"Error processing chunk {idx+1}: {type(e).__name__}: {e}", "ERROR", node=NODE_NAME)
                continue  # Skip this chunk on error

        state["unified_terminology"] = all_terms
        log_to_state(state, f"Unified terminology extraction complete. Total unique terms: {len(all_terms)}", "INFO", node=NODE_NAME)

    except Exception as e:
        log_to_state(state, f"Critical error in terminology_unification: {type(e).__name__}: {e}", "CRITICAL", node=NODE_NAME)
        state["unified_terminology"] = []

    return state