import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck(filename="Railway_Passenger_HelpDesk_Presentation.pptx"):
    prs = Presentation()
    # Modern 16:9 Widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Elegant Light Mode Color Palette
    BG_COLOR = RGBColor(248, 250, 252)       # Soft off-white / slate-50
    CARD_BG = RGBColor(255, 255, 255)        # Pure crisp white card
    CARD_BORDER = RGBColor(226, 232, 240)    # Slate-200 border
    PRIMARY_NAVY = RGBColor(15, 44, 89)      # Deep Railway Navy #0F2C59
    ACCENT_BLUE = RGBColor(26, 86, 219)      # Vibrant Blue #1A56DB
    ACCENT_TEAL = RGBColor(14, 148, 136)     # Slate Teal #0E9488
    TEXT_MAIN = RGBColor(30, 41, 59)         # Slate-800
    TEXT_MUTED = RGBColor(100, 116, 139)     # Slate-500
    TAG_BG = RGBColor(238, 242, 255)         # Indigo-50
    TAG_TEXT = RGBColor(67, 56, 202)         # Indigo-700
    SUCCESS_GREEN = RGBColor(16, 185, 129)   # Emerald-500

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background() # No border

    def add_header(slide, tag_text, title_text, subtitle_text):
        # Category Tag Pill
        tag_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.55), Inches(2.5), Inches(0.38))
        tag_box.fill.solid()
        tag_box.fill.fore_color.rgb = TAG_BG
        tag_box.line.color.rgb = RGBColor(199, 210, 254)
        tag_box.line.width = Pt(1)
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        p_tag = tf_tag.paragraphs[0]
        p_tag.alignment = PP_ALIGN.CENTER
        run_tag = p_tag.add_run()
        run_tag.text = tag_text.upper()
        run_tag.font.name = "Arial"
        run_tag.font.size = Pt(11)
        run_tag.font.bold = True
        run_tag.font.color.rgb = TAG_TEXT

        # Title Box
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.95), Inches(11.7), Inches(0.6))
        tf = title_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Arial"
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_NAVY

        # Subtitle
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.55), Inches(11.7), Inches(0.4))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.name = "Arial"
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = TEXT_MUTED

    card_w = Inches(3.7)
    card_h = Inches(4.2)
    top_pos = Inches(2.7)

    # ==========================================
    # SLIDE 1: INTRODUCTION & ARCHITECTURE
    # ==========================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1)

    hero_pill = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(3.2), Inches(0.4))
    hero_pill.fill.solid()
    hero_pill.fill.fore_color.rgb = RGBColor(224, 231, 255)
    hero_pill.line.fill.background()
    p_hp = hero_pill.text_frame.paragraphs[0]
    p_hp.alignment = PP_ALIGN.CENTER
    r_hp = p_hp.add_run()
    r_hp.text = "SYNAPSE FIVE • CAPSTONE PROJECT"
    r_hp.font.bold = True
    r_hp.font.size = Pt(11)
    r_hp.font.color.rgb = ACCENT_BLUE

    t_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(1.2))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Indian Railway Passenger Help Desk"
    p1.font.name = "Arial"
    p1.font.size = Pt(34)
    p1.font.bold = True
    p1.font.color.rgb = PRIMARY_NAVY

    p2 = tf1.add_paragraph()
    p2.text = "End-to-End Multilingual Agent: Hybrid Vector RAG & Strict Read-Only Text-to-SQL"
    p2.font.name = "Arial"
    p2.font.size = Pt(16)
    p2.font.color.rgb = ACCENT_TEAL
    p2.space_before = Pt(8)

    cols_data_1 = [
        ("The Passenger Problem", ACCENT_BLUE, [
            ("Dual Query Nature", "Passengers ask both legal policy questions (cancellation fees, Tatkal, 60-day ARP) and real-time operational timetable questions."),
            ("Information Friction", "Rules are buried inside scanned government PDFs and Gazette amendments across multiple years (2015-2026)."),
            ("Hallucination Risk", "Generic LLMs fabricate cancellation refund amounts and invented platform numbers.")
        ]),
        ("Our Hybrid Architecture", PRIMARY_NAVY, [
            ("Smart Intent Router", "Single entry point in ask.py routes incoming queries using strict intent heuristics and 5-digit train number detection."),
            ("ChromaDB Vector Store", "Indexes 145 hierarchical circular chunks using 384-dimensional dense semantic ONNX embeddings."),
            ("Strict Read-Only SQL Engine", "Queries 417,000+ schedules and 5,208 trains directly in SQLite via read-only URIs.")
        ]),
        ("Key Value Delivered", ACCENT_TEAL, [
            ("Zero Hallucinations", "Hard-grounded system prompt refuses to invent facts. Returns strict 'I don't know' with flag."),
            ("Bilingual & Hinglish", "Seamlessly answers Devanagari Hindi and colloquial Hinglish inquiries."),
            ("Enterprise Read-Only", "Blocks SQL write/injection risks (DROP, ALTER, UPDATE) before query execution.")
        ])
    ]

    for idx, (head, color, bullets) in enumerate(cols_data_1):
        left_pos = Inches(0.8 + idx * 4.0)
        card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, top_pos, card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1.5)

        hbar = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos + Inches(0.2), top_pos + Inches(0.25), card_w - Inches(0.4), Inches(0.5))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = RGBColor(241, 245, 249)
        hbar.line.fill.background()
        p_hb = hbar.text_frame.paragraphs[0]
        p_hb.alignment = PP_ALIGN.CENTER
        r_hb = p_hb.add_run()
        r_hb.text = head
        r_hb.font.bold = True
        r_hb.font.size = Pt(13)
        r_hb.font.color.rgb = color

        tb = slide1.shapes.add_textbox(left_pos + Inches(0.25), top_pos + Inches(0.9), card_w - Inches(0.5), Inches(3.1))
        tf_c = tb.text_frame
        tf_c.word_wrap = True
        for b_idx, (b_title, b_desc) in enumerate(bullets):
            p_b = tf_c.add_paragraph() if b_idx > 0 else tf_c.paragraphs[0]
            p_b.space_before = Pt(10)
            r_bt = p_b.add_run()
            r_bt.text = f"• {b_title}: "
            r_bt.font.bold = True
            r_bt.font.size = Pt(11)
            r_bt.font.color.rgb = TEXT_MAIN
            r_bd = p_b.add_run()
            r_bd.text = b_desc
            r_bd.font.size = Pt(10.5)
            r_bd.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 2: DATA INGESTION & VECTOR STORAGE
    # ==========================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2)
    add_header(slide2, "Phase 1: Ingestion & Indexing", "Document Extraction, Hierarchical Chunking & ChromaDB", 
               "Transforming fragmented Railway Board Circulars, Gazette notifications, and PIB web releases into dense semantic vectors.")

    cols_data_2 = [
        ("1. Multi-Format Extraction", PRIMARY_NAVY, [
            ("Native PDF Parsing", "Extracted clean high-density text from native digital circulars using PyPDF."),
            ("RapidOCR Fallback", "Executed local OCR for scanned notifications (e.g. Gazette notifications & CC 10/2025 charts)."),
            ("HTML DOM Cleaning", "Cleaned Gazette and PIB press releases using BeautifulSoup4, stripping navigation artifacts.")
        ]),
        ("2. Rule-Aware Chunking", ACCENT_BLUE, [
            ("Preserving Clause Hierarchy", "Avoided arbitrary token splitting. Kept cancellation rule slabs (e.g. >48h, 48-12h, <8h) intact."),
            ("Purna-Viram Splitting", "Applied Devanagari full stop (।) sentence segmentation for authentic Hindi circular processing."),
            ("Metadata Enrichment", "Each chunk preserves exact document name, page number, authority circular code, and date.")
        ]),
        ("3. Dense Vector Storage", ACCENT_TEAL, [
            ("Local 384-d Embeddings", "Embedded 145 chunks using Chroma's ONNX all-MiniLM-L6-v2 model (zero cost, zero latency)."),
            ("Cosine Similarity HNSW", "Built persistent vector collection 'railway_passenger_rules' with HNSW cosine indexing."),
            ("Sub-Second Retrieval", "Top-K retrieval executes in under 20ms with exact metadata filtering support.")
        ])
    ]

    for idx, (head, color, bullets) in enumerate(cols_data_2):
        left_pos = Inches(0.8 + idx * 4.0)
        card = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, top_pos, card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1.5)

        hbar = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos + Inches(0.2), top_pos + Inches(0.25), card_w - Inches(0.4), Inches(0.5))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = RGBColor(241, 245, 249)
        hbar.line.fill.background()
        p_hb = hbar.text_frame.paragraphs[0]
        p_hb.alignment = PP_ALIGN.CENTER
        r_hb = p_hb.add_run()
        r_hb.text = head
        r_hb.font.bold = True
        r_hb.font.size = Pt(13)
        r_hb.font.color.rgb = color

        tb = slide2.shapes.add_textbox(left_pos + Inches(0.25), top_pos + Inches(0.9), card_w - Inches(0.5), Inches(3.1))
        tf_c = tb.text_frame
        tf_c.word_wrap = True
        for b_idx, (b_title, b_desc) in enumerate(bullets):
            p_b = tf_c.add_paragraph() if b_idx > 0 else tf_c.paragraphs[0]
            p_b.space_before = Pt(10)
            r_bt = p_b.add_run()
            r_bt.text = f"• {b_title}: "
            r_bt.font.bold = True
            r_bt.font.size = Pt(11)
            r_bt.font.color.rgb = TEXT_MAIN
            r_bd = p_b.add_run()
            r_bd.text = b_desc
            r_bd.font.size = Pt(10.5)
            r_bd.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 3: TEXT-TO-SQL & STRICT READ-ONLY ENGINE
    # ==========================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3)
    add_header(slide3, "Phase 2: Timetable Engine", "Read-Only Text-to-SQL Over 417,000+ Railway Records", 
               "Answering operational queries on schedules, stations, and route sequences with zero hallucination and strict security guardrails.")

    cols_data_3 = [
        ("1. Timetable Database Schema", PRIMARY_NAVY, [
            ("trains (5,208 Rows)", "Stores train number, name, origin, destination, standard duration, and coach availability (1A, 2A, 3A, SL, CC)."),
            ("stations (8,990 Rows)", "Indexed railway codes (NDLS, MAS, SBC), station names, state, latitude, and longitude."),
            ("schedules (417,080 Rows)", "Sequential stop order, arrival/departure timestamps, and halt durations."),
            ("stops View", "Pre-filtered view WHERE is_halt = 1 for lightning-fast origin-destination route lookups.")
        ]),
        ("2. Read-Only Security Guardrails", RGBColor(220, 38, 38), [
            ("Strict SELECT / WITH Only", "Query validator regex ensures queries start strictly with read-only keywords."),
            ("Keyword Blacklisting", "Instantly rejects commands containing INSERT, UPDATE, DELETE, DROP, ALTER, EXEC, PRAGMA."),
            ("URI Read-Only Mode", "Enforces SQLite connection string flag ?mode=ro at OS socket level to prevent DB modification.")
        ]),
        ("3. Query Routing & Output", ACCENT_TEAL, [
            ("Regex & Intent Routing", "Queries matching 5-digit train numbers or 'fastest train', 'timings' trigger the SQL pipeline."),
            ("LLM Text-to-SQL Synthesis", "Gemini translates natural language into optimized multi-table JOINs (trains + schedules + stations)."),
            ("Transparent JSON Result", "Returns structured timetable data in 'answer' and populates 'sql_query' for user auditability.")
        ])
    ]

    for idx, (head, color, bullets) in enumerate(cols_data_3):
        left_pos = Inches(0.8 + idx * 4.0)
        card = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, top_pos, card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1.5)

        hbar = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos + Inches(0.2), top_pos + Inches(0.25), card_w - Inches(0.4), Inches(0.5))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = RGBColor(241, 245, 249)
        hbar.line.fill.background()
        p_hb = hbar.text_frame.paragraphs[0]
        p_hb.alignment = PP_ALIGN.CENTER
        r_hb = p_hb.add_run()
        r_hb.text = head
        r_hb.font.bold = True
        r_hb.font.size = Pt(13)
        r_hb.font.color.rgb = color

        tb = slide3.shapes.add_textbox(left_pos + Inches(0.25), top_pos + Inches(0.9), card_w - Inches(0.5), Inches(3.1))
        tf_c = tb.text_frame
        tf_c.word_wrap = True
        for b_idx, (b_title, b_desc) in enumerate(bullets):
            p_b = tf_c.add_paragraph() if b_idx > 0 else tf_c.paragraphs[0]
            p_b.space_before = Pt(8)
            r_bt = p_b.add_run()
            r_bt.text = f"• {b_title}: "
            r_bt.font.bold = True
            r_bt.font.size = Pt(11)
            r_bt.font.color.rgb = TEXT_MAIN
            r_bd = p_b.add_run()
            r_bd.text = b_desc
            r_bd.font.size = Pt(10)
            r_bd.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 4: EVALUATION METHODOLOGY (BM25 vs COSINE vs HNSW) - [NEW SLIDE]
    # ==========================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4)
    add_header(slide4, "Phase 3: Retrieval Evaluation", "How We Evaluated Retrieval: BM25 vs. Cosine Similarity vs. HNSW", 
               "Systematic benchmarking of sparse lexical retrieval against dense vector indexing to isolate search precision and recall.")

    cols_data_4 = [
        ("1. Lexical BM25 / Keyword Check", PRIMARY_NAVY, [
            ("Term-Frequency Search", "Evaluated traditional BM25/keyword matching over raw document tokens as our initial baseline."),
            ("The Lexical Gap", "Failed on synonyms (e.g. 'refund' vs 'cancellation fee'), Hindi Devanagari queries, and colloquial phrasing ('pehle book')."),
            ("Baseline Outcome", "Yielded a low 50% Hit Rate and 0.50 MRR because minor query phrasing variations bypassed lexical matches.")
        ]),
        ("2. Cosine Similarity on Embeddings", ACCENT_BLUE, [
            ("Dense Vector Space", "Mapped queries and circular chunks into 384-dimensional continuous vector space using all-MiniLM-L6-v2."),
            ("Dot Product Cosine Metric", "Evaluated angle distance: cos(θ) = (A · B) / (||A|| ||B||) to capture pure semantic intent regardless of exact wording."),
            ("Cross-Lingual Matching", "Allowed Devanagari Hindi and Hinglish queries to align directly with official Gazette English/Hindi clauses.")
        ]),
        ("3. HNSW Index Optimization", ACCENT_TEAL, [
            ("Hierarchical Navigable Small World", "ChromaDB indexes vectors via multi-layer HNSW graphs for approximate nearest neighbor (ANN) search."),
            ("Sub-20ms Search Latency", "Logarithmic search time O(log N) avoids exhaustive linear scans across large document corpora."),
            ("Evaluation Finding", "HNSW Cosine Search delivered 100% Hit Rate @ 3 and 1.000 MRR, retrieving the exact authority circular at Rank 1.")
        ])
    ]

    for idx, (head, color, bullets) in enumerate(cols_data_4):
        left_pos = Inches(0.8 + idx * 4.0)
        card = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, top_pos, card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1.5)

        hbar = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos + Inches(0.2), top_pos + Inches(0.25), card_w - Inches(0.4), Inches(0.5))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = RGBColor(241, 245, 249)
        hbar.line.fill.background()
        p_hb = hbar.text_frame.paragraphs[0]
        p_hb.alignment = PP_ALIGN.CENTER
        r_hb = p_hb.add_run()
        r_hb.text = head
        r_hb.font.bold = True
        r_hb.font.size = Pt(13)
        r_hb.font.color.rgb = color

        tb = slide4.shapes.add_textbox(left_pos + Inches(0.25), top_pos + Inches(0.9), card_w - Inches(0.5), Inches(3.1))
        tf_c = tb.text_frame
        tf_c.word_wrap = True
        for b_idx, (b_title, b_desc) in enumerate(bullets):
            p_b = tf_c.add_paragraph() if b_idx > 0 else tf_c.paragraphs[0]
            p_b.space_before = Pt(10)
            r_bt = p_b.add_run()
            r_bt.text = f"• {b_title}: "
            r_bt.font.bold = True
            r_bt.font.size = Pt(11)
            r_bt.font.color.rgb = TEXT_MAIN
            r_bd = p_b.add_run()
            r_bd.text = b_desc
            r_bd.font.size = Pt(10.5)
            r_bd.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 5: ZERO HALLUCINATION ARCHITECTURE
    # ==========================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5)
    add_header(slide5, "Phase 4: Trust & Safety", "Zero-Hallucination Architecture & Grounded Generation", 
               "Preventing invented train rules, fabricated refunds, and incorrect platform numbers through a multi-layered verification defense.")

    cols_data_5 = [
        ("Layer 1: Closed-Book Grounding", ACCENT_BLUE, [
            ("Strict Context Limitation", "The prompt explicitly instructs the LLM: 'Answer the question using ONLY the provided document chunks below.'"),
            ("Mandatory 'I Don't Know'", "If chunks lack the answer (e.g. platform numbers, unrecorded fares), the LLM must emit 'I don't know'."),
            ("Automated Status Flag", "The pipeline automatically flags dont_know: true and clears source citations to maintain truthfulness.")
        ]),
        ("Layer 2: Source Page Provenance", PRIMARY_NAVY, [
            ("Exact Page Citations", "Every answer for policy queries cites the exact source file and page (e.g. rb_cc10_2024_advance_reservation.pdf, Page 1)."),
            ("Auditable Reasoning", "Passengers and officials can verify the exact government clause behind any cancellation calculation."),
            ("Transparent Provenance", "If an answer is derived from multiple circulars, all relevant pages are returned in the sources array.")
        ]),
        ("Layer 3: Temporal Recency Overrides", ACCENT_TEAL, [
            ("Conflict Resolution", "Railway refund rules change frequently (2015 -> 2024 -> 2026). Our prompt explicitly enforces: 'Newer circulars override older rules'."),
            ("Example: 60-Day ARP", "Correctly enforces the 60-day limit from CC 10/2024, overruling legacy 120-day chunks from 2015."),
            ("Example: Vande Bharat", "Applies Gazette 2026 cancellation slabs (72h/8h rules) rather than general mail/express rules.")
        ])
    ]

    for idx, (head, color, bullets) in enumerate(cols_data_5):
        left_pos = Inches(0.8 + idx * 4.0)
        card = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, top_pos, card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1.5)

        hbar = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos + Inches(0.2), top_pos + Inches(0.25), card_w - Inches(0.4), Inches(0.5))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = RGBColor(241, 245, 249)
        hbar.line.fill.background()
        p_hb = hbar.text_frame.paragraphs[0]
        p_hb.alignment = PP_ALIGN.CENTER
        r_hb = p_hb.add_run()
        r_hb.text = head
        r_hb.font.bold = True
        r_hb.font.size = Pt(13)
        r_hb.font.color.rgb = color

        tb = slide5.shapes.add_textbox(left_pos + Inches(0.25), top_pos + Inches(0.9), card_w - Inches(0.5), Inches(3.1))
        tf_c = tb.text_frame
        tf_c.word_wrap = True
        for b_idx, (b_title, b_desc) in enumerate(bullets):
            p_b = tf_c.add_paragraph() if b_idx > 0 else tf_c.paragraphs[0]
            p_b.space_before = Pt(10)
            r_bt = p_b.add_run()
            r_bt.text = f"• {b_title}: "
            r_bt.font.bold = True
            r_bt.font.size = Pt(11)
            r_bt.font.color.rgb = TEXT_MAIN
            r_bd = p_b.add_run()
            r_bd.text = b_desc
            r_bd.font.size = Pt(10.5)
            r_bd.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 6: EVALUATION METRICS & BENCHMARK RESULTS (HIT RATE, MRR, RAGAS)
    # ==========================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6)
    add_header(slide6, "Phase 5: Quantitative Validation", "End-to-End Evaluation Metrics & Benchmark Performance", 
               "Systematic verification across 10 multi-category benchmark questions using IR metrics and Ragas-aligned context grounding.")

    # 4 Metric Stat Cards (Top row)
    metric_cards = [
        ("HIT RATE @ 3", "100.0%", "Relevant circular found in top 3 retrieved chunks for all test queries.", SUCCESS_GREEN),
        ("MRR", "1.0000", "Mean Reciprocal Rank: authoritative circular retrieved at Rank 1.", ACCENT_BLUE),
        ("PRECISION @ 3", "96.67%", "Signal-to-noise ratio: irrelevant chunks successfully filtered.", PRIMARY_NAVY),
        ("CONTEXT PRECISION", "100.0%", "Relevant context chunks consistently outrank background noise.", ACCENT_TEAL)
    ]

    m_w = Inches(2.7)
    m_h = Inches(1.8)
    for m_idx, (m_label, m_val, m_desc, m_col) in enumerate(metric_cards):
        m_left = Inches(0.8 + m_idx * 2.95)
        m_card = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, m_left, Inches(2.3), m_w, m_h)
        m_card.fill.solid()
        m_card.fill.fore_color.rgb = CARD_BG
        m_card.line.color.rgb = CARD_BORDER
        m_card.line.width = Pt(1.5)

        tf_m = m_card.text_frame
        tf_m.word_wrap = True
        tf_m.margin_left = tf_m.margin_right = tf_m.margin_top = tf_m.margin_bottom = Inches(0.12)
        
        p_val = tf_m.paragraphs[0]
        p_val.alignment = PP_ALIGN.CENTER
        r_val = p_val.add_run()
        r_val.text = m_val
        r_val.font.bold = True
        r_val.font.size = Pt(26)
        r_val.font.color.rgb = m_col

        p_lbl = tf_m.add_paragraph()
        p_lbl.alignment = PP_ALIGN.CENTER
        r_lbl = p_lbl.add_run()
        r_lbl.text = m_label
        r_lbl.font.bold = True
        r_lbl.font.size = Pt(10)
        r_lbl.font.color.rgb = TEXT_MUTED

        p_desc = tf_m.add_paragraph()
        p_desc.alignment = PP_ALIGN.CENTER
        p_desc.space_before = Pt(4)
        r_desc = p_desc.add_run()
        r_desc.text = m_desc
        r_desc.font.size = Pt(8.5)
        r_desc.font.color.rgb = TEXT_MAIN

    # Bottom Comparison Table: Baseline vs Optimized
    table_card = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.35), Inches(11.7), Inches(2.6))
    table_card.fill.solid()
    table_card.fill.fore_color.rgb = CARD_BG
    table_card.line.color.rgb = CARD_BORDER
    table_card.line.width = Pt(1.5)

    tb_t = slide6.shapes.add_textbox(Inches(1.0), Inches(4.45), Inches(11.3), Inches(2.4))
    tf_tbl = tb_t.text_frame
    tf_tbl.word_wrap = True

    p_th = tf_tbl.paragraphs[0]
    r_th = p_th.add_run()
    r_th.text = "Baseline (Naive BM25 & Unrouted) vs. Final Optimized System (Hybrid ChromaDB + Text-to-SQL)"
    r_th.font.bold = True
    r_th.font.size = Pt(13)
    r_th.font.color.rgb = PRIMARY_NAVY

    rows = [
        ("Hit Rate @ 3", "50.0%", "100.0%", "+50.0%", "Cosine vector search captures synonyms, Devanagari Hindi, and circular aliases."),
        ("Mean Reciprocal Rank (MRR)", "0.500", "1.000", "+0.500", "Authoritative circular retrieved at Rank 1 on every single test case."),
        ("Precision @ 3", "46.7%", "96.7%", "+50.0%", "Intent routing prevents timetable inquiries from contaminating document search."),
        ("Context Recall", "48.6%", "86.3%", "+37.7%", "Rule-aware hierarchical chunking preserves complete multi-tier refund slabs."),
        ("Ragas Framework Ready", "N/A", "Active", "Complete", "Built-in pipeline with fallback ensuring zero crash on restricted environments.")
    ]

    for m_name, base, opt, diff, reason in rows:
        p_r = tf_tbl.add_paragraph()
        p_r.space_before = Pt(5)
        r1 = p_r.add_run()
        r1.text = f"• {m_name:<28}: "
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = TEXT_MAIN

        r2 = p_r.add_run()
        r2.text = f"{base}  ➔  {opt} ({diff})  |  "
        r2.font.bold = True
        r2.font.size = Pt(10)
        r2.font.color.rgb = ACCENT_BLUE

        r3 = p_r.add_run()
        r3.text = reason
        r3.font.size = Pt(9.5)
        r3.font.color.rgb = TEXT_MUTED

    prs.save(filename)
    print(f"Presentation successfully created at: {os.path.abspath(filename)}")

if __name__ == "__main__":
    create_deck()
