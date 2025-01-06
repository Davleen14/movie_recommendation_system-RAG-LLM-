# Movie Recommendation System

This system provides personalized movie recommendations using data from the TMDB API, MongoDB Atlas, and an LLM-powered engine. The backend handles data ingestion, vector search, query processing, advanced filtering, and history tracking.

---
## Technology Stack Summary

### Frontend
| Technology       | Purpose                                                |
|-------------------|--------------------------------------------------------|
| **Next.js**       | Framework for building the React frontend.             |
| **Tailwind CSS**  | Utility-first CSS framework for rapid and responsive UI design. |
| **ReactMarkdown** | Rendering LLM recommendations in markdown format.      |
| **Flask API**     | Integration for fetching recommendations and history data. |

### Backend
| Technology             | Purpose                                                |
|-------------------------|--------------------------------------------------------|
| **Flask**              | Backend framework to handle queries and manage APIs.   |
| **MongoDB Atlas**      | Database for storing movie data, embeddings, and user history. |
| **TMDB API**           | Fetching popular movies and genre data.                |
| **SentenceTransformer**| Generating vector embeddings for movie titles and overviews. |
| **Groq API**           | Integration with `llama-3.3-70b-versatile` LLM for recommendations. |
| **spaCy**              | Processing user queries and extracting keywords.        |

# Working of Backend 

## Step 1: Data Ingestion (`process_data.py`)

The `process_data.py` script is responsible for ingesting movie data into the MongoDB Atlas database. It leverages the TMDB API to fetch popular movies and their metadata. Here's a detailed overview of its functionality:

1. **Fetch Movie Genres**:
   - The script retrieves genre information from the TMDB API using the [Genre List API](https://api.themoviedb.org/3/genre/movie/list). 
   - This allows mapping genre IDs to human-readable names.

2. **Fetch Popular Movies**:
   - Popular movies are fetched from the TMDB API using the [Popular Movies API](https://api.themoviedb.org/3/movie/popular).
   - The script processes these movies and filters out adult content to ensure appropriate data ingestion.

3. **Generate Embeddings**:
   - The script uses the `SentenceTransformer` model (`all-MiniLM-L6-v2`) to generate embeddings for movie titles and overviews.
   - These embeddings are essential for similarity-based recommendations.

4. **Store Data in MongoDB**:
   - Each movie's metadata and embeddings, along with genre information, are compiled into a document and upserted into the `movies` collection of the MongoDB Atlas database.

5. **Execution**:
   - The `seed_database_from_tmdb` function orchestrates the process:
     - Fetches genres once.
     - Iterates through multiple pages of movie data.

**Usage**:
- Run `process_data.py` to populate the database with movie data.
- Ensure the TMDB API key is configured in the script.

---

## Step 2: Query Processing and Recommendations (`app.py`)

The `app.py` file implements the backend logic, handling user queries, advanced filtering, and generating personalized movie recommendations.

### Key Steps

1. **Vector Search for Similar Movies**:
   - The system uses MongoDB Atlas's vector index (`movie_index`) to perform similarity searches.
   - Queries are encoded into vectors using the `SentenceTransformer` model (`all-MiniLM-L6-v2`), and movies with the most similar embeddings are retrieved.
   - **Advanced Filtering**: Filters like "top-rated," "popular," "recent," and "old" are applied here as well, refining results based on user input.
   - **Function**: `retrieve_similar_movies(query, n=5)`

2. **Retrieve Movies by Genre**:
   - Matches the user's query to predefined genres and fetches movies accordingly.
   - Advanced filters are also applied here to narrow results:
     - **Top-rated**: Movies with `vote_average >= 8.5`
     - **Popular**: Movies with `vote_count >= 500`
     - **Recent**: Movies released after January 1, 2020.
     - **Old**: Movies released before January 1, 1990.
   - **Function**: `retrieve_similar_movies_by_genre(genre, n=150, query="")`

3. **Advanced Filtering**:
   - Advanced filtering is applied in both vector search for similar movies and genre-based searches.
   - Extracted filters:
     - `"top-rated"` or `"high-rated"`: Filters for movies with high ratings.
     - `"popular"`: Filters for movies with a high vote count.
     - `"recent"`: Filters for newer releases.
     - `"old"`: Filters for older movies.
   - This ensures precise results, tailored to user preferences.
   - **Function**: `parse_advanced_filters(query)`

4. **Query Processing**:
   - User input is processed using the `spaCy` NLP library to extract meaningful keywords.
   - Keywords help match genres or improve the relevance of vector search results.
   - **Function**: `process_query(query)`

5. **Handle User Queries**:
   - Combines all features to process user queries:
     - Matches genres or retrieves similar movies using vector search.
     - Applies **Advanced Filtering** for precision.
     - Calls `converse_with_llm` to generate a recommendation based on retrieved movies.
     - Saves the query and results in the `search_history` collection for future reference.
   - **Function**: `handle_query()`

6. **Search History**:
   - Stores user queries and their corresponding recommendations in the `search_history` collection.
   - **Function**: `get_history()`

---

## Step 3: Recommendation Generation (`generator.py`)

The `generator.py` file integrates a Large Language Model (LLM) via the **Groq API** to generate personalized movie recommendations.

### LLM Integration

- The **LLM used** is `llama-3.3-70b-versatile`.
- The `converse_with_llm` function communicates with the LLM to create a personalized recommendation.
- The LLM uses metadata about similar movies and the user's query to provide meaningful recommendations.

### How It Works

1. A list of similar movies (from vector search or genre matching) is passed to the LLM.
2. A prompt is generated to provide context and ask for a recommendation.

## Summary

- **Step 1 (Data Ingestion)**: Fetch and store movie data and embeddings in MongoDB Atlas.
- **Step 2 (Query Handling)**: Process user queries, retrieve similar movies, and apply filters.
- **Step 3 (Recommendation)**: Use the LLM (`llama-3.3-70b-versatile`) to generate personalized movie suggestions.



## Working of Frontend: User Interface

The frontend of the Movie Recommendation System is built using the following technologies:

1. **Next.js**

2. **Tailwind CSS**
   
3. **Flask Backend Integration**
   - The frontend communicates with the Flask backend API to fetch data.
   - Endpoints:
     - **`POST /api/query`**: Fetches movie recommendations based on user input.
     - **`GET /api/history`**: Retrieves the search history.

### Key Features of the Frontend

1. **Search Functionality**:
   - Users can enter a query (e.g., "Recommend a top-rated sci-fi movie").
   - Pressing **Enter** or clicking "Get Recommendations" triggers a backend API call to fetch movie recommendations.

2. **Interactive History**:
   - Search history is fetched from the backend and displayed in a dropdown menu.
   - Users can click on a history item to re-run the query.

3. **Loading Indicator**:
   - A spinner is displayed while the system processes the request, ensuring users know the app is working.

4. **Recommendations Display**:
   - Recommendations from the LLM are displayed in a markdown-rendered format.
   - A grid of similar movies is displayed with:
     - Movie poster.
     - Title and release year.
     - Overview (truncated if long).
     - Rating and vote count.

5. **Responsive Design**:
   - The layout adapts seamlessly for mobile, tablet, and desktop devices using Tailwind CSS's responsive utilities.

### Example Frontend Workflow

1. **User Input**:
   - The user enters a query like "Find me a popular romantic movie."
   - This input is sent to the Flask backend API.

2. **Fetching Recommendations**:
   - The backend processes the query and returns:
     - A recommendation generated by the LLM.
     - A list of similar movies based on vector search and filters.

3. **Displaying Results**:
   - The frontend displays:
     - A markdown-rendered LLM recommendation.
     - A grid of similar movies with their details.

## API Endpoints

### 1. `POST /api/query`
- **Description**: Processes a user query and returns similar movies along with a personalized recommendation.
- **Input**: JSON with a `query` field containing the user's search query.
- **Output**: A list of similar movies and a recommendation generated by the LLM.

---

### 2. `GET /api/history`
- **Description**: Retrieves the history of user queries and their results.
- **Input**: None.
- **Output**: A list of past queries made by the user.

## API Keys and Configuration

All sensitive keys and configuration details are securely stored in the `apikey.py` file and accessed as environment variables. These include:

1. **TMDB API Key**:
   - Used to interact with the TMDB API for fetching movie data such as genres and popular movies.

2. **MongoDB Connection String**:
   - Connects the application to the MongoDB Atlas database for storing movie metadata, embeddings, and user query history.

3. **Groq Cloud API Key**:
   - Used for integration with the Groq Cloud API to call the `llama-3.3-70b-versatile` Large Language Model (LLM) for generating personalized recommendations.

### Environment Variable Usage

- The keys stored in `apikey.py` are accessed as environment variables in the application.
- Ensure that the `apikey.py` file is properly configured with the required keys:
  ```python
  TMDB_API_KEY = "your_tmdb_api_key_here"
  MONGO_CONNECTION_STRING = "your_mongo_connection_string_here"
  GROQ_API_KEY = "your_groq_api_key_here"



