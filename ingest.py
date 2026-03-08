#!/usr/bin/env python3
"""
ARA Ingestor - Fat Prompt, Thin Client

A thin client that converts ArXiv papers into Agent-Native Research Artifacts (ARA).
Uses a comprehensive system prompt to guide LLM extraction of structured knowledge.

Supports both OpenAI and Google Gemini APIs.

Usage:
    python ingest.py <arxiv_id> [--output_dir <dir>] [--model <model>] [--provider <provider>]
    
Example:
    python ingest.py 2404.16283 --output_dir andes_ara_output
    python ingest.py 2404.16283 --output_dir andes_ara_output --provider gemini
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional, List, Tuple

import requests

# Add temp pip packages to path
sys.path.insert(0, '/tmp/pip_packages')


def fetch_arxiv_html(arxiv_id: str) -> str:
    """
    Fetch paper content from ArXiv HTML endpoint.
    
    Args:
        arxiv_id: ArXiv paper ID (e.g., '2404.16283')
        
    Returns:
        Extracted text content from the paper
    """
    # Try the ArXiv HTML endpoint first (ar5iv)
    html_url = f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}"
    
    print(f"[INFO] Fetching paper from: {html_url}")
    
    try:
        response = requests.get(html_url, timeout=60)
        response.raise_for_status()
        
        # Extract text from HTML
        from html.parser import HTMLParser
        
        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text_parts = []
                self.in_script = False
                self.in_style = False
                self.in_nav = False
                
            def handle_starttag(self, tag, attrs):
                if tag == 'script':
                    self.in_script = True
                elif tag == 'style':
                    self.in_style = True
                elif tag == 'nav':
                    self.in_nav = True
                    
            def handle_endtag(self, tag):
                if tag == 'script':
                    self.in_script = False
                elif tag == 'style':
                    self.in_style = False
                elif tag == 'nav':
                    self.in_nav = False
                    
            def handle_data(self, data):
                if not self.in_script and not self.in_style and not self.in_nav:
                    text = data.strip()
                    if text:
                        self.text_parts.append(text)
        
        extractor = TextExtractor()
        extractor.feed(response.text)
        
        text = '\n'.join(extractor.text_parts)
        
        # Clean up excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        print(f"[INFO] Successfully extracted {len(text)} characters from HTML")
        return text
        
    except requests.RequestException as e:
        print(f"[WARN] HTML fetch failed: {e}")
        print("[INFO] Falling back to abstract endpoint...")
        return fetch_arxiv_abstract(arxiv_id)


def fetch_arxiv_abstract(arxiv_id: str) -> str:
    """
    Fallback: Fetch paper abstract and metadata from ArXiv API.
    
    Args:
        arxiv_id: ArXiv paper ID
        
    Returns:
        Paper abstract and metadata
    """
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    
    print(f"[INFO] Fetching from ArXiv API: {api_url}")
    
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()
    
    # Simple XML parsing for abstract
    content = response.text
    
    # Extract title
    title_match = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
    title = title_match.group(1).strip() if title_match else "Unknown Title"
    
    # Extract abstract
    abstract_match = re.search(r'<summary>(.*?)</summary>', content, re.DOTALL)
    abstract = abstract_match.group(1).strip() if abstract_match else "No abstract available"
    
    # Extract authors
    authors = re.findall(r'<name>(.*?)</name>', content)
    
    text = f"""
Title: {title}

Authors: {', '.join(authors)}

Abstract:
{abstract}

Note: Full paper text could not be fetched. This is the abstract only.
"""
    
    print(f"[INFO] Extracted abstract ({len(text)} characters)")
    return text


def load_system_prompt(prompt_path: str = "ara_system_prompt.txt") -> str:
    """
    Load the ARA system prompt from file.
    
    Args:
        prompt_path: Path to the system prompt file
        
    Returns:
        System prompt content
    """
    script_dir = Path(__file__).parent
    full_path = script_dir / prompt_path
    
    if not full_path.exists():
        raise FileNotFoundError(f"System prompt not found: {full_path}")
    
    with open(full_path, 'r', encoding='utf-8') as f:
        return f.read()


def call_openai(system_prompt: str, paper_text: str, model: str = "gpt-4o") -> str:
    """
    Send the paper to OpenAI API for ARA extraction.
    
    Args:
        system_prompt: The ARA system prompt
        paper_text: The research paper content
        model: OpenAI model to use
        
    Returns:
        LLM response containing ARA file structure
    """
    from openai import OpenAI
    
    client = OpenAI()  # Uses OPENAI_API_KEY env var
    
    print(f"[INFO] Sending to OpenAI {model}...")
    print(f"[INFO] Paper length: {len(paper_text)} chars")
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": paper_text}
        ],
        max_tokens=16000,
        temperature=0.2  # Low temperature for consistent extraction
    )
    
    result = response.choices[0].message.content
    print(f"[INFO] Received response: {len(result)} chars")
    
    return result


def call_gemini(system_prompt: str, paper_text: str, model: str = "gemini-2.5-flash") -> str:
    """
    Send the paper to Google Gemini API for ARA extraction.
    
    Args:
        system_prompt: The ARA system prompt
        paper_text: The research paper content
        model: Gemini model to use
        
    Returns:
        LLM response containing ARA file structure
    """
    import google.generativeai as genai
    
    # Configure API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        # Try loading from .env file
        env_path = Path(__file__).parent.parent.parent / '.env'
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment or .env file")
    
    genai.configure(api_key=api_key)
    
    print(f"[INFO] Sending to Gemini {model}...")
    print(f"[INFO] Paper length: {len(paper_text)} chars")
    
    # Create model with system instruction
    gen_model = genai.GenerativeModel(
        model_name=model,
        system_instruction=system_prompt
    )
    
    # Generate response
    response = gen_model.generate_content(
        paper_text,
        generation_config=genai.types.GenerationConfig(
            temperature=0.2,
            max_output_tokens=16000,
        )
    )
    
    result = response.text
    print(f"[INFO] Received response: {len(result)} chars")
    
    return result


def call_llm(system_prompt: str, paper_text: str, provider: str = "openai", model: str = None) -> str:
    """
    Send the paper to the specified LLM provider for ARA extraction.
    
    Args:
        system_prompt: The ARA system prompt
        paper_text: The research paper content
        provider: LLM provider ('openai' or 'gemini')
        model: Model name (defaults based on provider)
        
    Returns:
        LLM response containing ARA file structure
    """
    if provider == "openai":
        model = model or "gpt-4o"
        return call_openai(system_prompt, paper_text, model)
    elif provider == "gemini":
        model = model or "gemini-2.5-flash"
        return call_gemini(system_prompt, paper_text, model)
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'openai' or 'gemini'")


def parse_files(response: str) -> List[Tuple[str, str]]:
    """
    Parse <file path="...">content</file> blocks from LLM response.
    
    Args:
        response: LLM response containing file blocks
        
    Returns:
        List of (path, content) tuples
    """
    # Pattern to match file blocks
    # Handles both <file path="..."> and <file path='...'>
    pattern = r'<file\s+path=["\']([^"\']+)["\']>(.*?)</file>'
    
    matches = re.findall(pattern, response, re.DOTALL)
    
    files = []
    for path, content in matches:
        # Clean up the content
        content = content.strip()
        # Normalize path (remove leading slashes)
        path = path.lstrip('/')
        files.append((path, content))
    
    print(f"[INFO] Parsed {len(files)} files from response")
    
    return files


def extract_deconstruction(response: str) -> Optional[str]:
    """
    Extract the deconstruction block from the response.
    
    Args:
        response: LLM response
        
    Returns:
        Deconstruction content or None
    """
    pattern = r'<deconstruction>(.*?)</deconstruction>'
    match = re.search(pattern, response, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    return None


def write_files(files: List[Tuple[str, str]], output_dir: str) -> None:
    """
    Safely create directories and write files.
    
    Args:
        files: List of (path, content) tuples
        output_dir: Base output directory
    """
    output_path = Path(output_dir)
    
    for file_path, content in files:
        # Create full path
        full_path = output_path / file_path
        
        # Security check: ensure path doesn't escape output directory
        try:
            full_path.resolve().relative_to(output_path.resolve())
        except ValueError:
            print(f"[WARN] Skipping suspicious path: {file_path}")
            continue
        
        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] Written: {file_path}")


def main():
    parser = argparse.ArgumentParser(
        description="ARA Ingestor - Convert ArXiv papers to Agent-Native Research Artifacts"
    )
    parser.add_argument(
        "arxiv_id",
        help="ArXiv paper ID (e.g., 2404.16283)"
    )
    parser.add_argument(
        "--output_dir",
        default="ara_output",
        help="Output directory for ARA files (default: ara_output)"
    )
    parser.add_argument(
        "--provider",
        default="gemini",
        choices=["openai", "gemini"],
        help="LLM provider to use (default: gemini)"
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model to use (default: gpt-4o for openai, gemini-2.5-flash for gemini)"
    )
    parser.add_argument(
        "--prompt",
        default="ara_system_prompt.txt",
        help="Path to system prompt file (default: ara_system_prompt.txt)"
    )
    parser.add_argument(
        "--save-response",
        action="store_true",
        help="Save raw LLM response to file"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ARA Ingestor - Fat Prompt, Thin Client")
    print("=" * 60)
    print(f"ArXiv ID: {args.arxiv_id}")
    print(f"Output: {args.output_dir}")
    print(f"Provider: {args.provider}")
    print(f"Model: {args.model or ('gpt-4o' if args.provider == 'openai' else 'gemini-2.5-flash')}")
    print("=" * 60)
    
    # Step 1: Fetch paper
    print("\n[STEP 1] Fetching paper...")
    paper_text = fetch_arxiv_html(args.arxiv_id)
    
    if not paper_text or len(paper_text) < 100:
        print("[ERROR] Failed to fetch paper content")
        sys.exit(1)
    
    # Step 2: Load system prompt
    print("\n[STEP 2] Loading system prompt...")
    system_prompt = load_system_prompt(args.prompt)
    print(f"[INFO] System prompt: {len(system_prompt)} chars")
    
    # Step 3: Call LLM
    print("\n[STEP 3] Processing with LLM...")
    try:
        response = call_llm(system_prompt, paper_text, args.provider, args.model)
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        sys.exit(1)
    
    # Optionally save raw response
    if args.save_response:
        response_file = Path(args.output_dir) / "_raw_response.md"
        response_file.parent.mkdir(parents=True, exist_ok=True)
        with open(response_file, 'w') as f:
            f.write(response)
        print(f"[INFO] Saved raw response to {response_file}")
    
    # Step 4: Extract deconstruction
    print("\n[STEP 4] Extracting deconstruction...")
    deconstruction = extract_deconstruction(response)
    if deconstruction:
        print(f"[OK] Found deconstruction block ({len(deconstruction)} chars)")
        # Save deconstruction as a file
        decon_path = Path(args.output_dir) / "_deconstruction.md"
        decon_path.parent.mkdir(parents=True, exist_ok=True)
        with open(decon_path, 'w') as f:
            f.write("# Paper Deconstruction\n\n")
            f.write(deconstruction)
        print(f"[OK] Saved deconstruction to {decon_path}")
    else:
        print("[WARN] No deconstruction block found")
    
    # Step 5: Parse and write files
    print("\n[STEP 5] Parsing and writing files...")
    files = parse_files(response)
    
    if not files:
        print("[ERROR] No files parsed from response")
        print("[DEBUG] Response preview:")
        print(response[:2000])
        sys.exit(1)
    
    write_files(files, args.output_dir)
    
    # Summary
    print("\n" + "=" * 60)
    print("ARA GENERATION COMPLETE")
    print("=" * 60)
    print(f"Output directory: {args.output_dir}")
    print(f"Files created: {len(files)}")
    
    # List structure
    print("\nARA Structure:")
    for path, _ in sorted(files):
        print(f"  {path}")
    
    print("\n[SUCCESS] ARA generation complete!")


if __name__ == "__main__":
    main()
