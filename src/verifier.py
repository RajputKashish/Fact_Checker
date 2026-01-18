"""Claim verification using web search and LLM analysis (Groq - FREE)."""

import json
from typing import List
from groq import Groq
from tavily import TavilyClient
from .models import Claim, VerificationResult, VerificationStatus, Source


VERIFICATION_PROMPT = """You are a fact-checking assistant. Your task is to verify if a claim is accurate based on the search results provided.

CLAIM TO VERIFY:
"{claim}"

CONTEXT FROM DOCUMENT:
"{context}"

SEARCH RESULTS:
{search_results}

Analyze the search results and determine if the claim is:
1. **VERIFIED** - The claim matches current, reliable data
2. **INACCURATE** - The claim contains outdated or slightly wrong information (e.g., old statistics, wrong dates, old GDP figures)
3. **FALSE** - The claim is demonstrably false or no credible evidence supports it

IMPORTANT: If the claim contains data from 2019 or earlier, and search results show different current data, mark it as INACCURATE and provide the correct current information.

Respond with a JSON object:
{{
    "status": "VERIFIED" | "INACCURATE" | "FALSE",
    "explanation": "Brief explanation of your verdict",
    "correct_info": "If inaccurate/false, provide the correct information here. Otherwise null.",
    "confidence": 0.0 to 1.0
}}

Be precise and cite specific data from the search results. If the search results don't contain relevant information, mark as FALSE with low confidence.
"""


def verify_claims(
    claims: List[Claim],
    groq_api_key: str,
    tavily_api_key: str,
    progress_callback=None
) -> List[VerificationResult]:
    """
    Verify a list of claims using web search and LLM analysis.
    
    Args:
        claims: List of claims to verify.
        groq_api_key: Groq API key.
        tavily_api_key: Tavily API key.
        progress_callback: Optional callback for progress updates.
        
    Returns:
        List of verification results.
    """
    groq_client = Groq(api_key=groq_api_key)
    tavily_client = TavilyClient(api_key=tavily_api_key)
    
    results = []
    
    for i, claim in enumerate(claims):
        if progress_callback:
            progress_callback(i + 1, len(claims), claim.text[:50] + "...")
        
        try:
            result = verify_single_claim(claim, groq_client, tavily_client)
            results.append(result)
        except Exception as e:
            # Create a failed verification result
            results.append(VerificationResult(
                claim=claim,
                status=VerificationStatus.PENDING,
                explanation=f"Verification failed: {str(e)}",
                confidence=0.0
            ))
    
    return results


def verify_single_claim(
    claim: Claim,
    groq_client: Groq,
    tavily_client: TavilyClient
) -> VerificationResult:
    """
    Verify a single claim.
    
    Args:
        claim: The claim to verify.
        groq_client: Groq client.
        tavily_client: Tavily client.
        
    Returns:
        Verification result.
    """
    # Search for information about the claim
    search_query = generate_search_query(claim)
    
    try:
        search_response = tavily_client.search(
            query=search_query,
            search_depth="advanced",
            max_results=5
        )
        
        search_results = format_search_results(search_response)
        sources = extract_sources(search_response)
        
    except Exception as e:
        raise ValueError(f"Search failed: {str(e)}")
    
    # Analyze with LLM
    prompt = VERIFICATION_PROMPT.format(
        claim=claim.text,
        context=claim.context,
        search_results=search_results
    )
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise fact-checker. Analyze claims against search results and provide accurate verdicts. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        verdict = parse_verdict(content)
        
        return VerificationResult(
            claim=claim,
            status=verdict["status"],
            explanation=verdict["explanation"],
            correct_info=verdict.get("correct_info"),
            sources=sources,
            confidence=verdict.get("confidence", 0.5)
        )
        
    except Exception as e:
        raise ValueError(f"LLM analysis failed: {str(e)}")


def generate_search_query(claim: Claim) -> str:
    """Generate an effective search query for a claim."""
    # Use the claim text directly, possibly shortened
    query = claim.text
    if len(query) > 200:
        query = query[:200]
    
    # Add verification-related terms for certain claim types
    if claim.claim_type == "financial":
        query += " current data 2024 2025"
    elif claim.claim_type == "statistic":
        query += " latest statistics 2024"
    
    return query


def format_search_results(response: dict) -> str:
    """Format Tavily search results for LLM consumption."""
    results = response.get("results", [])
    
    if not results:
        return "No search results found."
    
    formatted = []
    for i, result in enumerate(results, 1):
        formatted.append(f"""
Source {i}: {result.get('title', 'Unknown')}
URL: {result.get('url', 'N/A')}
Content: {result.get('content', 'No content available')}
""")
    
    return "\n".join(formatted)


def extract_sources(response: dict) -> List[Source]:
    """Extract source information from search results."""
    results = response.get("results", [])
    sources = []
    
    for result in results[:3]:  # Top 3 sources
        sources.append(Source(
            title=result.get("title", "Unknown"),
            url=result.get("url", ""),
            snippet=result.get("content", "")[:200] + "..."
        ))
    
    return sources


def parse_verdict(content: str) -> dict:
    """Parse the LLM verdict response."""
    content = content.strip()
    
    # Remove markdown code blocks if present
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
    
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON from the text
        import re
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            try:
                data = json.loads(match.group())
            except:
                data = {}
        else:
            data = {}
    
    # Map status string to enum
    status_map = {
        "VERIFIED": VerificationStatus.VERIFIED,
        "INACCURATE": VerificationStatus.INACCURATE,
        "FALSE": VerificationStatus.FALSE
    }
    
    status_str = data.get("status", "FALSE").upper()
    status = status_map.get(status_str, VerificationStatus.FALSE)
    
    return {
        "status": status,
        "explanation": data.get("explanation", "Could not determine verdict"),
        "correct_info": data.get("correct_info"),
        "confidence": float(data.get("confidence", 0.5))
    }
