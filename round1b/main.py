# round1b/main.py - FINAL CORRECTED VERSION

import fitz
import json
import os
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import datetime
from collections import Counter

# --- CONFIGURATION ---
INPUT_DIR = '/app/input'
OUTPUT_DIR = '/app/output'
MODEL_PATH = '/app/model'
TOP_N_SECTIONS = 5
RELEVANCE_THRESHOLD = 0.2

# --- ROBUST HEADING EXTRACTION (ROUND 1A LOGIC) ---
def get_document_stats(doc):
    font_sizes = Counter()
    if doc.page_count == 0: return 12
    for page in doc:
        text_page = page.get_text("dict", flags=0)
        for block in text_page["blocks"]:
            if block['type'] == 0 and "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_sizes[round(span["size"])] += 1
    return font_sizes.most_common(1)[0][0] if font_sizes else 12

def extract_headings(doc):
    body_font_size = get_document_stats(doc)
    headings = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks", sort=True)
        for b in blocks:
            if b[6] == 0: # Text block
                text = re.sub(r'\s+', ' ', b[4]).strip()
                if not text or len(text.split()) > 30: continue
                
                block_dict = page.get_text("dict", clip=b[:4], flags=0)["blocks"]
                if not (block_dict and block_dict[0]['lines'] and block_dict[0]['lines'][0]['spans']):
                    continue
                
                span = block_dict[0]['lines'][0]['spans'][0]
                size = round(span['size'])
                is_bold = (span['flags'] & 2**4) > 0

                # A heading is larger than body text OR it is bold.
                if (size > body_font_size) or (is_bold and size >= body_font_size):
                     headings.append({'text': text, 'page': page_num + 1, 'y_pos': b[1]})

    headings.sort(key=lambda x: (x['page'], x['y_pos']))
    return headings

# --- ROUND 1B LOGIC ---
def parse_input_json(input_dir):
    input_json_path = os.path.join(input_dir, 'challenge1b_input.json')
    with open(input_json_path, 'r', encoding='utf-8') as f: data = json.load(f)
    persona = data.get('persona', {}).get('role', data.get('persona', ''))
    job_to_be_done = data.get('job_to_be_done', {}).get('task', data.get('job_to_be_done', ''))
    query = f"Based on my role as a {persona}, I need to '{job_to_be_done}'"
    return query, data

def process_pdfs_for_chunks(input_dir, model):
    pdf_files_dir = os.path.join(input_dir, 'PDFs')
    if not os.path.isdir(pdf_files_dir):
        return [], None
        
    pdf_files = [f for f in os.listdir(pdf_files_dir) if f.lower().endswith('.pdf')]
    all_chunks = []
    
    for pdf_file in pdf_files:
        path = os.path.join(pdf_files_dir, pdf_file)
        doc = fitz.open(path)
        headings = extract_headings(doc)
        
        for page_num, page in enumerate(doc):
            blocks = page.get_text("blocks")
            for b in blocks:
                if b[6] == 0:
                    para = re.sub(r'\s+', ' ', b[4]).strip()
                    if len(para) > 50:
                        current_heading = "General Information"
                        block_y_pos = b[1]
                        relevant_headings = [h for h in headings if h['page'] == page_num + 1 and h['y_pos'] < block_y_pos]
                        if relevant_headings:
                            current_heading = relevant_headings[-1]['text']
                        else:
                            relevant_headings_prev_pages = [h for h in headings if h['page'] < page_num + 1]
                            if relevant_headings_prev_pages:
                                current_heading = relevant_headings_prev_pages[-1]['text']
                        all_chunks.append({
                            'document': pdf_file,
                            'page_number': page_num + 1,
                            'text': para,
                            'section_title': current_heading
                        })
        doc.close()
        
    if not all_chunks: return [], None
    chunk_texts = [chunk['text'] for chunk in all_chunks]
    chunk_embeddings = model.encode(chunk_texts, show_progress_bar=False, batch_size=32)
    return all_chunks, chunk_embeddings

def find_relevant_sections(query, all_chunks, chunk_embeddings, model):
    if not all_chunks: return []
    query_embedding = model.encode([query], show_progress_bar=False)
    similarities = cosine_similarity(query_embedding, chunk_embeddings)[0]
    for i, chunk in enumerate(all_chunks):
        chunk['relevance'] = similarities[i]
        
    relevant_chunks = [c for c in sorted(all_chunks, key=lambda x: x['relevance'], reverse=True) if c['relevance'] > RELEVANCE_THRESHOLD]
    return relevant_chunks

def generate_output(input_data, relevant_chunks, output_dir):
    # --- DIVERSIFICATION LOGIC ---
    # Find the single most relevant chunk from each document
    top_chunk_per_doc = {}
    for chunk in relevant_chunks:
        doc = chunk['document']
        if doc not in top_chunk_per_doc:
            top_chunk_per_doc[doc] = chunk
    
    # Now, sort these top chunks by their relevance to get a diverse list
    diverse_top_chunks = sorted(top_chunk_per_doc.values(), key=lambda x: x['relevance'], reverse=True)

    # --- STANDARD OUTPUT GENERATION ---
    unique_sections = {}
    for chunk in diverse_top_chunks: # Use the diverse list
        key = (chunk['document'], chunk['section_title'])
        if key not in unique_sections:
            unique_sections[key] = {
                "document": chunk['document'],
                "page_number": chunk['page_number'],
                "section_title": chunk['section_title'],
                "relevance": chunk['relevance']
            }

    sorted_sections = sorted(unique_sections.values(), key=lambda x: x['relevance'], reverse=True)

    extracted_sections = []
    for i, section in enumerate(sorted_sections[:TOP_N_SECTIONS]):
        extracted_sections.append({
            "document": section['document'],
            "section_title": section['section_title'],
            "importance_rank": i + 1,
            "page_number": section['page_number']
        })
        
    subsection_analysis = []
    for chunk in diverse_top_chunks[:TOP_N_SECTIONS]: # Use the diverse list
        subsection_analysis.append({
            "document": chunk['document'],
            "refined_text": chunk['text'],
            "page_number": chunk['page_number']
        })

    output_data = {
        "metadata": {
            "input_documents": [doc['filename'] for doc in input_data.get('documents', [])],
            "persona": input_data.get('persona', {}).get('role', input_data.get('persona', '')),
            "job_to_be_done": input_data.get('job_to_be_done', {}).get('task', input_data.get('job_to_be_done', '')),
            "processing_timestamp": datetime.datetime.now().isoformat()
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }
    
    output_path = os.path.join(output_dir, 'challenge1b_output.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    print(f"Successfully created output at {output_path}")

if __name__ == '__main__':
    model = SentenceTransformer(MODEL_PATH)
    query, input_data = parse_input_json(INPUT_DIR)
    all_chunks, chunk_embeddings = process_pdfs_for_chunks(INPUT_DIR, model)
    relevant_chunks = find_relevant_sections(query, all_chunks, chunk_embeddings, model)
    generate_output(input_data, relevant_chunks, OUTPUT_DIR)