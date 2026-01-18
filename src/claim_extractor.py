"""Claim extraction using LLM (Groq - FREE)."""

import json
import os
import streamlit as st
from typing import List, Tuple
from groq import Groq
from .models import Claim


CLAIM_EXTRACTION_PROMPT = """You are a fact-checking assistant. Your task is to extract specific, verifiable claims from the given text.

Focus on extracting claims that contain:
1. **Statistics and numerical data** (percentages, counts, measurements, GDP figures, growth rates)
2. **Dates and temporal claims** (when something happened, timelines, years)
3. **Financial figures** (prices, market caps, revenue, GDP, stock prices, economic forecasts)
4. **Technical specifications** (product specs, scientific data)
5. **Factual assertions** (who did what, where, historical facts, organizational details)

IMPORTANT: Extract ALL numerical claims, economic data, percentages, and dates you find. Be thorough.

For each claim, provide:
- The exact claim text as stated in the document
- The surrounding context (1-2 sentences before/after)
- The type of claim (statistic, date, financial, technical, factual)

Return your response as a JSON array with this structure:
[
    {
        "claim": "The exact claim text with specific numbers/dates",
        "context": "Surrounding context for better understanding",
        "claim_type": "statistic|date|financial|technical|factual"
    }
]

Extract at least 5-10 claims if the text contains numerical or factual data. Do NOT skip economic data, GDP figures, percentages, or dates.

TEXT TO ANALYZE:
"""


def extract_claims(pages: List[Tuple[int, str]], api_key: str) -> List[Claim]:
    """
    Extract claims from PDF pages using Groq LLM (FREE).
    
    Args:
        pages: List of (page_number, text) tuples.
        api_key: Groq API key.
        
    Returns:
        List of extracted claims.
    """
    client = Groq(api_key=api_key)
    all_claims = []
    
    # Process pages in batches to get more context
    combined_text = ""
    page_map = {}
    
    for page_num, text in pages:
        if not text.strip():
            continue
        
        start_pos = len(combined_text)
        combined_text += f"\n\n--- Page {page_num} ---\n\n{text}"
        page_map[start_pos] = page_num
    
    if not combined_text.strip():
        st.warning("No text content found in PDF")
        return []
    
    # Process in chunks if too long
    chunks = []
    if len(combined_text) > 12000:
        # Split into chunks of ~10000 chars
        for i in range(0, len(combined_text), 10000):
            chunk = combined_text[i:i+12000]
            chunks.append(chunk)
    else:
        chunks = [combined_text]
    
    st.info(f"Processing {len(chunks)} text chunk(s) using Groq (FREE)...")
    
    for chunk_idx, chunk in enumerate(chunks):
        try:
            st.text(f"Analyzing chunk {chunk_idx + 1}/{len(chunks)}...")
            
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Fast, free model
                messages=[
                    {
                        "role": "system",
                        "content": "You are a thorough fact-checking assistant. Extract ALL verifiable claims containing numbers, dates, percentages, or specific facts. Be comprehensive - extract at least 5-10 claims from economic or data-rich documents. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": CLAIM_EXTRACTION_PROMPT + chunk
                    }
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            
            # Debug: show raw response
            with st.expander(f"Debug: Raw LLM Response (chunk {chunk_idx + 1})"):
                st.code(content[:2000] + "..." if len(content) > 2000 else content)
            
            # Parse JSON response
            claims_data = parse_claims_json(content)
            
            st.text(f"Found {len(claims_data)} claims in chunk {chunk_idx + 1}")
            
            for claim_data in claims_data:
                claim = Claim(
                    text=claim_data.get("claim", ""),
                    context=claim_data.get("context", ""),
                    page_number=1,  # Default to page 1 for combined processing
                    claim_type=claim_data.get("claim_type", "factual")
                )
                if claim.text:
                    all_claims.append(claim)
                    
        except Exception as e:
            st.error(f"Error extracting claims from chunk {chunk_idx + 1}: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            continue
    
    return all_claims


def parse_claims_json(content: str) -> List[dict]:
    """
    Parse JSON from LLM response, handling potential formatting issues.
    
    Args:
        content: Raw LLM response.
        
    Returns:
        List of claim dictionaries.
    """
    import re
    
    # Try to find JSON array in the response
    content = content.strip()
    
    # Remove markdown code blocks if present
    if "```json" in content:
        match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
        if match:
            content = match.group(1)
    elif content.startswith("```"):
        lines = content.split("\n")
        # Remove first and last lines (``` markers)
        if lines[-1].strip() == "```":
            content = "\n".join(lines[1:-1])
        else:
            content = "\n".join(lines[1:])
    
    content = content.strip()
    
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError as e:
        # Try to extract JSON array from the text
        match = re.search(r'\[\s*\{[\s\S]*\}\s*\]', content)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        
        # Last resort: try to find any array
        match = re.search(r'\[[\s\S]*\]', content)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        
        return []
