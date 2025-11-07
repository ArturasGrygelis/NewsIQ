import Link from 'next/link'
import { Newspaper, MessageCircle, Database } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Newspaper className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-2xl font-bold text-gray-900">NewsIQ</span>
            </div>
            <div className="flex space-x-4">
              <Link href="/" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                Home
              </Link>
              <Link href="/app" className="bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium">
                Launch App
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          <h1 className="text-5xl font-extrabold text-gray-900 sm:text-6xl md:text-7xl">
            Intelligent News
            <span className="block text-blue-600">Knowledge Base</span>
          </h1>
          <p className="mt-6 max-w-2xl mx-auto text-xl text-gray-600">
            Ingest, analyze, and query news articles with AI-powered insights. 
            Build your personalized knowledge base from the latest news sources.
          </p>
          <div className="mt-10">
            <Link href="/app" className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:text-lg">
              Get Started
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mt-24 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-600 text-white mb-4">
              <Database className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Article Ingestion</h3>
            <p className="text-gray-600">
              Import articles directly from URLs or search by topic across multiple news sources. 
              Automatic content extraction and processing.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-600 text-white mb-4">
              <MessageCircle className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Intelligent Q&A</h3>
            <p className="text-gray-600">
              Ask questions about your ingested articles and receive AI-powered answers 
              with source citations and relevant context.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-600 text-white mb-4">
              <Newspaper className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Vector Search</h3>
            <p className="text-gray-600">
              Powered by ChromaDB vector store for semantic search. 
              Find relevant information across thousands of articles instantly.
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white mt-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-500 text-sm">
            © 2025 NewsIQ. Powered by LangGraph, FastAPI, and Next.js.
          </p>
        </div>
      </footer>
    </div>
  )
}
