# main.py in round1a/ - FINAL PRODUCTION VERSION (Corrected Title Logic)

import fitz
import os
import json
import re
from collections import Counter

# --- CONFIGURATION ---
INPUT_DIR = '/app/input'
OUTPUT_DIR = '/app/output'

def get_doc_properties(doc):
    """Gathers overall statistics and properties of the document."""
    stats = {
        'total_words': 0,
        'font_sizes': Counter(),
        'avg_words_per_line': 0
    }
    line_count = 0
    for page in doc:
        text_page = page.get_text("dict", flags=0)
        for block in text_page["blocks"]:
            if block['type'] == 0 and "lines" in block:
                for line in block["lines"]:
                    line_count += 1
                    line_text = " ".join(span['text'] for span in line['spans'])
                    stats['total_words'] += len(line_text.split())
                    for span in line["spans"]:
                        stats['font_sizes'][round(span["size"])] += 1
    
    stats['body_font_size'] = stats['font_sizes'].most_common(1)[0][0] if stats['font_sizes'] else 12
    if line_count > 0:
        stats['avg_words_per_line'] = stats['total_words'] / line_count
    
    # Context detection
    stats['is_form_like'] = stats['avg_words_per_line'] > 0 and stats['avg_words_per_line'] < 5
    stats['is_sparse'] = stats['total_words'] < 200 # Likely an invitation or flyer
    
    return stats

def extract_structure(pdf_path):
   """ Analyzes a given PDF file to extract its title and hierarchical outline.
      Args:
        pdf_path (str): The full path to the PDF file to be processed.
       Returns:
        dict: A dictionary containing the 'title' and a list of 'outline' items.
              Returns None if the document cannot be processed."""
   try:
        doc = fitz.open(pdf_path)
   except Exception as e:
        return {"title": os.path.basename(pdf_path), "outline": []}

   if doc.page_count == 0:
        return {"title": os.path.basename(pdf_path), "outline": []}

   doc_props = get_doc_properties(doc)
    
   candidates = []
   for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks", sort=True)
        for b in blocks:
            if b[6] == 0: # Text blocks
                text = re.sub(r'\s+', ' ', b[4]).strip()
                if not text: continue

                block_dict = page.get_text("dict", clip=b[:4], flags=0)["blocks"]
                if not (block_dict and block_dict[0]['lines'] and block_dict[0]['lines'][0]['spans']):
                    continue
                span = block_dict[0]['lines'][0]['spans'][0]
                
                size = round(span['size'])
                is_bold = (span['flags'] & 2**4) > 0 or "bold" in span['font'].lower()
                
                score = 0
                if size > doc_props['body_font_size']:
                    score += (size - doc_props['body_font_size']) * 2
                if is_bold:
                    score += 4
                if re.match(r'^\d+(\.\d+)*\s', text) or re.match(r'^[A-Z]\.\s', text) or re.match(r'^Appendix\s[A-Z]:', text):
                    score += 10
                if text.isupper() and len(text) > 10:
                    score += 2
                
                if doc_props['is_form_like'] and len(text.split()) < 4:
                    score = 0
                if doc_props['is_sparse'] and size > doc_props['body_font_size'] * 1.5:
                    score += 15

                if score > 3:
                    candidates.append({'text': text, 'score': score, 'page': page_num + 1, 'y_pos': b[1]})

   if not candidates:
        # If no candidates, it's a doc with no headings (like file01 after filtering)
        # Try to find a title before returning
        title_text = ""
        first_page_blocks = doc[0].get_text("blocks", sort=True)
        if first_page_blocks:
            # Assume title is one of the first few blocks at the top of page 1
            top_blocks = sorted([b for b in first_page_blocks if b[6]==0], key=lambda b: b[1])[:3]
            if top_blocks:
                title_text = " ".join(re.sub(r'\s+', ' ', b[4]).strip() for b in top_blocks if len(b[4]) > 5)

        return {"title": title_text or os.path.basename(pdf_path), "outline": []}

   unique_scores = sorted(list(set(c['score'] for c in candidates)), reverse=True)
   score_to_level = {}
   level_map = ["H1", "H2", "H3", "H4", "H5"]
   for i, score in enumerate(unique_scores[:len(level_map)]):
        score_to_level[score] = level_map[i]
        
   outline = []
   for c in candidates:
        if c['score'] in score_to_level:
            outline.append({'level': score_to_level[c['score']], 'text': c['text'], 'page': c['page'], 'y_pos': c['y_pos']})

   title = ""
   if doc_props['is_sparse']:
        # For sparse docs like invitations, force an empty title
        title = ""
   else:
        first_page_candidates = [c for c in candidates if c['page'] == 1]
        if first_page_candidates:
            first_page_candidates.sort(key=lambda c: c['y_pos'])
            title = first_page_candidates[0]['text']
            outline = [item for item in outline if not (item['text'] == title and item['page'] == 1)]
    
   if not title and not doc_props['is_sparse']:
        title = os.path.basename(pdf_path)

   final_outline = [{'level': i['level'], 'text': i['text'], 'page': i['page']} for i in outline]
   final_outline.sort(key=lambda x: (x['page'], {'H1':1, 'H2':2, 'H3':3, 'H4':4, 'H5':5}.get(x['level'], 99)))

   doc.close()
   return {"title": title, "outline": final_outline}

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(INPUT_DIR, filename)
            print(f"Processing {pdf_path}...")
            structure = extract_structure(pdf_path)
            if structure:
                output_filename = os.path.splitext(filename)[0] + '.json'
                output_path = os.path.join(OUTPUT_DIR, output_filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(structure, f, indent=4, ensure_ascii=False)
                print(f"Successfully created {output_path}")