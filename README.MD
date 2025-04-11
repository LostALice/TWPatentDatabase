# 台灣經濟部智慧財產局專利檢索系統爬蟲

# Update Log

## V0.2 update 28/3/2025
### Add installation guide and AI-related dependencies; disable Milvus handlers

- Updated `README.md` to include steps for using `uv` for package management.
- Added dependencies including `einops`, `pymilvus`, `sentence-transformers`, and `transformers` to support NLP and vector database functionalities.
- Commented out `insert_sentence` and `search_similarity` methods in `vector_database.py`—likely part of a temporary pause or refactor of Milvus-based operations.

## V0.1 update 20/3/2025
### Initialize backend utilities and frontend project setup  

- Added vector database handlers in `Backend/utility/handler/` and `Backend/utility/model/handler/`.  
- Initialized the frontend project with Next.js, including essential configuration files.  
- Added frontend components such as `navbar.tsx`, `theme-switch.tsx`, and `transition.tsx`.  
- Configured ESLint, TypeScript, and Tailwind for frontend development.  
- Included project documentation (`README.md`, `LICENSE`).  
