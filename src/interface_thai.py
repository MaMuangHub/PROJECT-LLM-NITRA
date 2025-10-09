# interface_thai.py
# Multi-language support for RAG Chat Application

# --- Thai Language Dictionary ---
THAI_TEXTS = {
    "APP_TITLE": "ผู้ช่วยแชท RAG",
    "HEADER_TITLE": "NITRA",
    "HEADER_SUBTITLE": "🌙 NITRA — ผู้ช่วยดูแลการนอนหลับของคุณในทุกค่ำคืน",
    "SIDEBAR_CONFIG_HEADER": "⚙️ ตั้งค่า",
    "MODEL_SELECT_LABEL": "🤖 เลือกโมเดล",
    "MODEL_SELECT_HELP": "เลือกโมเดลที่ใช้",
    "TEMP_SLIDER_LABEL": "🌡️ ระดับความคิดสร้างสรรค์",
    "TEMP_SLIDER_HELP": "ควบคุมความสุ่มของการตอบกลับ",
    "MAX_TOKENS_LABEL": "📏 โทเคนสูงสุด",
    "MAX_TOKENS_HELP": "ความยาวสูงสุดของการตอบกลับ",
    "RAG_SETTINGS_HEADER": "📚 ตั้งค่า RAG",
    "CONTEXT_MAX_TOKENS_LABEL": "โทเคนของบริบท",
    "CONTEXT_MAX_TOKENS_HELP": "โทเคนบริบทสูงสุดที่จะส่งไปให้ LLM",
    "SEARCH_RESULTS_LABEL": "จำนวนผลการค้นหา",
    "SEARCH_RESULTS_HELP": "จำนวนข้อมูล (Chunk) ที่จะดึงขึ้นมา",
    "INIT_MODEL_BUTTON": "🤖 เริ่มต้น Model",
    "INIT_RAG_BUTTON": "📚 เริ่มต้น RAG",
    "INIT_MODEL_SPINNER": "กำลังเริ่มต้น Model...",
    "INIT_RAG_SPINNER": "กำลังเริ่มต้นระบบ RAG...",
    "INIT_MODEL_SUCCESS": "Model พร้อมใช้งาน!",
    "INIT_RAG_SUCCESS": "ระบบ RAG พร้อมใช้งาน!",
    "DOC_MANAGEMENT_HEADER": "📁 จัดการเอกสาร",
    "FILE_UPLOADER_LABEL": "อัปโหลดเอกสาร",
    "FILE_UPLOADER_HELP": "อัปโหลดไฟล์ข้อความหรือ PDF เพื่อเพิ่มในคลังความรู้",
    "ADD_TEXT_EXPANDER": "✏️ เพิ่มเอกสารข้อความ",
    "DOC_TITLE_INPUT": "ชื่อเอกสาร",
    "DOC_CONTENT_INPUT": "เนื้อหาเอกสาร",
    "ADD_DOC_BUTTON": "เพิ่มเอกสารข้อความ",
    "ADD_DOC_SUCCESS": "เพิ่มเอกสาร: ",
    "LOAD_SAMPLE_BUTTON": "📖 โหลดเอกสารตัวอย่าง",
    "CLEAR_CHAT_BUTTON": "🗑️ เคลียแชท",
    "STATS_HEADER": "📊 สถิติ",
    "STATS_DOCUMENTS": "เอกสารทั้งหมด",
    "STATS_CHUNKS": "ข้อมูล (Chunks)",
    "ABOUT_HEADER": "📚 เกี่ยวกับ",
    "ABOUT_FEATURES_HEADER": "**คุณสมบัติ (Features):**",
    "ABOUT_FEATURES": """
    - อัปโหลดไฟล์ PDF และข้อความ 
    - การค้นหาเชิงความหมายในเอกสาร
    - การตอบกลับของ AI ที่มีบริบท
    - การจัดการเอกสาร
    """,
    "ABOUT_STUDENTS_HEADER": "**สำหรับนักเรียน/นักพัฒนา:**",
    "ABOUT_STUDENTS": """
    - ทดลองกับระบบ Embeddings
    - กลยุทธ์การแบ่งส่วนข้อมูล (Chunking) ขั้นสูง
    - การกรองข้อมูลเมตา (Metadata)
    - ระบบการอ้างอิง
    """,
    "TAB_CHAT": "💬 แชท",
    "TAB_DOCUMENTS": "📄 เอกสาร",
    "WELCOME_TITLE": "🚀 ยินดีต้อนรับสู่ RAG Chat",
    "WELCOME_MESSAGE": "อัปโหลดเอกสารของคุณและเริ่มถามคำถามได้เลย! ผู้ช่วย AI ของเราจะค้นหาข้อมูลจากคลังความรู้ของคุณและให้คำตอบที่แม่นยำและสอดคล้องกับบริบท",
    "WELCOME_FEATURES_LIST": """
    <ul style="margin-top: 15px;">
        <li>📄 อัปโหลดไฟล์ PDF และข้อความ</li>
        <li>🔍 การค้นหาเชิงความหมายอัจฉริยะ</li>
        <li>💡 การตอบกลับของ AI ที่มีบริบท</li>
        <li>📚 จัดการคลังความรู้ของคุณ</li>
    </ul>
    """,
    "WELCOME_WARNING": "⚠️ กรุณาเริ่มต้นทั้ง Model และระบบ RAG ในแถบด้านข้าง (Sidebar) ก่อน!",
    "EX_QUERY_HEADER": "❔ วันนี้คุณมีปัญหาการนอนหลับอย่างไร:",
    "EX_QUERY_1": "💤 ฉันรู้สึกนอนไม่หลับเลยวันนี้",
    "EX_QUERY_2": "😴 ฉันควรนอนกี่ชั่วโมง?",
    "EX_QUERY_3": "🛏️ บอกวิธีนอนหลับให้ดีหน่อย",
    "CHAT_INPUT_PLACEHOLDER": "💬 ถามอะไรก็ได้เกี่ยวกับการนอนหลับ...",
    "ASSISTANT_SPINNER": "🔍 กำลังค้นหาเอกสารและสร้างคำตอบ...",
    "RETRIEVED_CONTEXT_EXPANDER": "📄 บริบทที่ดึงมา",
    "DOC_KB_HEADER": "📄 เอกสารในคลังความรู้",
    "NO_DOCS_INFO": "ยังไม่มีเอกสารในคลังความรู้",
    "CONTEXT_USED": "📚 *ใช้ข้อมูลจากเอกสาร*",
    "ASSISTANT_ROLE": "assistant",
    "USER_ROLE": "user",
    "DELETE_BUTTON_LABEL": "ลบ",
    "ADD_FILE_BUTTON_LABEL": "เพิ่ม",
    "PROCESSING_FILE": "กำลังประมวลผล",
    "FILE_ADD_SUCCESS": "เพิ่มไฟล์ข้อความสำเร็จ:",
    "FILE_ERROR": "เกิดข้อผิดพลาดในการประมวลผล",
    "LANG_BUTTON": "🇬🇧 English",
}

# --- English Language Dictionary ---
ENGLISH_TEXTS = {
    "APP_TITLE": "RAG Chat Assistant",
    "HEADER_TITLE": "NITRA",
    "HEADER_SUBTITLE": "🌙 NITRA — Your Sleep Companion for Every Night",
    "SIDEBAR_CONFIG_HEADER": "⚙️ Configuration",
    "MODEL_SELECT_LABEL": "🤖 Select Language Model",
    "MODEL_SELECT_HELP": "Choose the language model to use",
    "TEMP_SLIDER_LABEL": "🌡️ Temperature",
    "TEMP_SLIDER_HELP": "Control the randomness of responses",
    "MAX_TOKENS_LABEL": "📏 Max Tokens",
    "MAX_TOKENS_HELP": "Maximum length of the response",
    "RAG_SETTINGS_HEADER": "📚 RAG Settings",
    "CONTEXT_MAX_TOKENS_LABEL": "Max Context Tokens",
    "CONTEXT_MAX_TOKENS_HELP": "Maximum tokens for context sent to LLM",
    "SEARCH_RESULTS_LABEL": "Number of Search Results",
    "SEARCH_RESULTS_HELP": "Number of chunks to retrieve",
    "INIT_MODEL_BUTTON": "🤖 Initialize Model",
    "INIT_RAG_BUTTON": "📚 Initialize RAG",
    "INIT_MODEL_SPINNER": "Initializing Model...",
    "INIT_RAG_SPINNER": "Initializing RAG System...",
    "INIT_MODEL_SUCCESS": "Model is ready!",
    "INIT_RAG_SUCCESS": "RAG System is ready!",
    "DOC_MANAGEMENT_HEADER": "📁 Document Management",
    "FILE_UPLOADER_LABEL": "Upload Documents",
    "FILE_UPLOADER_HELP": "Upload text or PDF files to add to the knowledge base",
    "ADD_TEXT_EXPANDER": "✏️ Add Text Document",
    "DOC_TITLE_INPUT": "Document Title",
    "DOC_CONTENT_INPUT": "Document Content",
    "ADD_DOC_BUTTON": "Add Text Document",
    "ADD_DOC_SUCCESS": "Added document: ",
    "LOAD_SAMPLE_BUTTON": "📖 Load Sample Documents",
    "CLEAR_CHAT_BUTTON": "🗑️ Clear Chat",
    "STATS_HEADER": "📊 Statistics",
    "STATS_DOCUMENTS": "Total Documents",
    "STATS_CHUNKS": "Total Chunks",
    "ABOUT_HEADER": "📚 About",
    "ABOUT_FEATURES_HEADER": "**Features:**",
    "ABOUT_FEATURES": """
    - Upload PDF and text files
    - Semantic search in documents
    - Context-aware AI responses
    - Document management
    """,
    "ABOUT_STUDENTS_HEADER": "**For Students/Developers:**",
    "ABOUT_STUDENTS": """
    - Experiment with Embeddings
    - Advanced Chunking Strategies
    - Metadata Filtering
    - Citation System
    """,
    "TAB_CHAT": "💬 Chat",
    "TAB_DOCUMENTS": "📄 Documents",
    "WELCOME_TITLE": "🚀 Welcome to RAG Chat",
    "WELCOME_MESSAGE": "Upload your documents and start asking questions! Our AI assistant will search through your knowledge base and provide accurate, context-aware answers.",
    "WELCOME_FEATURES_LIST": """
    <ul style="margin-top: 15px;">
        <li>📄 Upload PDF and text files</li>
        <li>🔍 Intelligent semantic search</li>
        <li>💡 Context-aware AI responses</li>
        <li>📚 Manage your knowledge base</li>
    </ul>
    """,
    "WELCOME_WARNING": "⚠️ Please initialize both Model and RAG System in the Sidebar first!",
    "EX_QUERY_HEADER": "❔ What's your sleep concern today:",
    "EX_QUERY_1": "💤 I can't sleep at all today",
    "EX_QUERY_2": "😴 How many hours should I sleep?",
    "EX_QUERY_3": "🛏️ Tell me how to sleep better",
    "CHAT_INPUT_PLACEHOLDER": "💬 Ask anything about sleep...",
    "ASSISTANT_SPINNER": "🔍 Searching documents and generating answer...",
    "RETRIEVED_CONTEXT_EXPANDER": "📄 Retrieved Context",
    "DOC_KB_HEADER": "📄 Documents in Knowledge Base",
    "NO_DOCS_INFO": "No documents in knowledge base yet",
    "CONTEXT_USED": "📚 *Using context from documents*",
    "ASSISTANT_ROLE": "assistant",
    "USER_ROLE": "user",
    "DELETE_BUTTON_LABEL": "Delete",
    "ADD_FILE_BUTTON_LABEL": "Add",
    "PROCESSING_FILE": "Processing",
    "FILE_ADD_SUCCESS": "Text file added successfully:",
    "FILE_ERROR": "Error processing",
    "LANG_BUTTON": "🇹🇭 ไทย",
}


def get_texts(language="th"):
    if language == "en":
        return ENGLISH_TEXTS
    return THAI_TEXTS