"use client";
import Image from "next/image";
import { useState, useEffect } from "react";
import { ClockIcon } from "@heroicons/react/16/solid";
import ReactMarkdown from "react-markdown";

export default function Home() {
  const [query, setQuery] = useState("");
  const [keywords, setKeywords] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    const fetchHistory = async () => {
      const response = await fetch("http://0.0.0.0:5001/api/history");
      const data = await response.json();
      setHistory(data);
    };
    fetchHistory();
  }, []);
  const handleSearch = async (langQuery) => {
    setLoading(true);
    if (!langQuery) {
      langQuery = query;
    }
    try {
      const response = await fetch("http://0.0.0.0:5001/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: langQuery }),
      });
      const data = await response.json();
      setResult(data);
      if (!history.includes(query)) {
        setHistory((prevHistory) => [...prevHistory, query]);
      }
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyUp = (event) => {
    if (event.key === "Enter") {
      handleSearch();
    }
  };
  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center px-2 pb-20 sm:px-20 font-[family-name:var(--font-geist-sans)]">
      <main
        className="flex flex-col gap-8 row-start-2 items-center sm:items-start"
        style={{ width: "-webkit-fill-available" }}
      >
        <div className="p-6" style={{ width: "-webkit-fill-available" }}>
          <h1 className="text-2xl font-bold mb-4 text-center">
            Movie Recommendation Engine
          </h1>
          <div className="flex items-center relative w-full mb-4">
            <input
              type="text"
              className="border p-2 w-full"
              placeholder="Enter your preferences (e.g., Recommend me a sci-fi movie)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ color: "black" }}
              onKeyUp={handleKeyUp}
              onFocus={() => setShowHistory(false)}
            />

            <div
              className="ml-2 cursor-pointer relative"
              onClick={() => setShowHistory(!showHistory)}
            >
              <ClockIcon className="w-6 h-6 text-gray-600" />

              {showHistory && (
                <ul className="absolute right-0 top-8 bg-white border border-gray-200 w-64 mt-1 rounded shadow-lg z-10 max-h-40 overflow-y-auto">
                  {history.length === 0 ? (
                    <li className="p-2 text-gray-500">No history available</li>
                  ) : (
                    history.map((item, index) => (
                      <li
                        key={index}
                        className="p-2 hover:bg-gray-100 cursor-pointer"
                        onClick={() => {
                          setQuery(item);
                          handleSearch(item);
                          setShowHistory(false);
                        }}
                        style={{ color: "black" }}
                      >
                        {item}
                      </li>
                    ))
                  )}
                </ul>
              )}
            </div>
          </div>

          <button
            className="bg-blue-500 text-white px-4 py-2"
            onClick={handleSearch}
            disabled={loading}
          >
            {loading ? "Loading..." : "Get Recommendations"}
          </button>

          {loading && (
            <div className="mt-6 text-center">
              <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="mt-2 text-gray-500">Fetching recommendations...</p>
            </div>
          )}

          {result && !loading && (
            <div className="mt-6">
              <div className="movie-recommendation">
                <h2> LLM Movie Recommendation</h2>
                <ReactMarkdown>{result.recommendation}</ReactMarkdown>
              </div>

              <h3 className="text-lg font-semibold mt-4 mb-6">Top Movies:</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {result.similar_movies
                  .filter((movie) => movie.vote_average != 0)
                  .map((movie, index) => (
                    <div
                      key={index}
                      className="bg-white shadow-md rounded-lg overflow-hidden border border-gray-200"
                    >
                      <img
                        src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                        alt={`${movie.title} poster`}
                        className="w-full h-64 object-cover"
                      />
                      <div className="p-4">
                        <h4 className="text-md font-semibold text-gray-800 truncate">
                          {movie.title}
                        </h4>
                        <p className="text-sm text-black-500 mt-0 py-0 my-0">
                          {movie.release_date?.split("-")[0]}
                        </p>
                        <p className="text-sm text-gray-600 mt-2">
                          {movie.overview.length > 100
                            ? `${movie.overview.substring(0, 100)}...`
                            : movie.overview}
                        </p>
                        <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                          <span>Rating: {movie.vote_average}/10</span>
                          <span>{movie.vote_count} Votes</span>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
