import { useState } from 'react'
import Link from 'next/link'
import { Newspaper, Send, Loader2, Database, Search, Link as LinkIcon } from 'lucide-react'
import axios from 'axios'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{
    title: string
    url: string
    snippet: string
    authors?: string
    language?: string
    topics?: string
  }>
}

export default function AppPage() {
  const [activeTab, setActiveTab] = useState<'chat' | 'ingest'>('chat')
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)

  // Ingest form state
  const [ingestType, setIngestType] = useState<'url' | 'search'>('search')
  const [articleUrl, setArticleUrl] = useState('')
  const [topic, setTopic] = useState('')
  const [website, setWebsite] = useState('')
  const [maxAge, setMaxAge] = useState(7)
  const [ingestLoading, setIngestLoading] = useState(false)
  const [ingestResult, setIngestResult] = useState<string | null>(null)
  const [ingestedArticle, setIngestedArticle] = useState<any>(null)

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await axios.post('/api/answer', {
        question: input,
        session_id: sessionId
      }, {
        timeout: 120000  // 2 minutes timeout for long-running workflows
      })

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources
      }

      setMessages(prev => [...prev, assistantMessage])
      setSessionId(response.data.session_id)
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the backend is running and try again.'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleIngest = async () => {
    setIngestLoading(true)
    setIngestResult(null)

    try {
      const payload = ingestType === 'url' 
        ? { article_url: articleUrl }
        : { topic, website: website || undefined, max_age_days: maxAge }

      const response = await axios.post('/api/ingest', payload, {
        timeout: 120000  // 2 minutes timeout
      })

      if (response.data.success) {
        const data = response.data
        setIngestResult(`✓ ${data.message}`)
        setIngestedArticle(data)
        // Clear form
        setArticleUrl('')
        setTopic('')
        setWebsite('')
        setMaxAge(7)
      } else {
        setIngestResult(`✗ ${response.data.message}`)
      }
    } catch (error) {
      setIngestResult('✗ Failed to ingest article. Please check the backend connection.')
    } finally {
      setIngestLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center">
              <Newspaper className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-2xl font-bold text-gray-900">NewsIQ</span>
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="flex space-x-4 mb-6 border-b">
          <button
            onClick={() => setActiveTab('chat')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'chat'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Chat & Questions
          </button>
          <button
            onClick={() => setActiveTab('ingest')}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === 'ingest'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Ingest Articles
          </button>
        </div>

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="flex gap-4 h-[calc(100vh-250px)]">
            {/* Main Chat Area */}
            <div className="flex-1 bg-white rounded-lg shadow-lg flex flex-col">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center text-gray-500 mt-12">
                    <Database className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                    <p className="text-lg font-medium">Ask questions about your articles</p>
                    <p className="text-sm mt-2">Start by ingesting some articles, then ask away!</p>
                  </div>
                )}

                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-3xl rounded-lg px-4 py-3 ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  </div>
                ))}

                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-lg px-4 py-3">
                      <Loader2 className="h-5 w-5 animate-spin text-gray-600" />
                    </div>
                  </div>
                )}
              </div>

              {/* Input */}
              <div className="border-t p-4">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Ask a question about your articles..."
                    className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
                    disabled={loading}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={loading || !input.trim()}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                  >
                    <Send className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Sources Sidebar */}
            <div className="w-96 bg-white rounded-lg shadow-lg overflow-hidden flex flex-col">
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-3">
                <h3 className="text-white font-semibold flex items-center">
                  <Database className="h-5 w-5 mr-2" />
                  Source Documents
                </h3>
              </div>
              
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages
                  .filter(msg => msg.role === 'assistant' && msg.sources && msg.sources.length > 0)
                  .slice(-1)[0]?.sources ? (
                  messages
                    .filter(msg => msg.role === 'assistant' && msg.sources && msg.sources.length > 0)
                    .slice(-1)[0].sources.map((source, idx) => (
                      <div key={idx} className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:border-blue-300 transition-colors">
                        <a 
                          href={source.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 font-semibold text-sm flex items-start gap-2 mb-2"
                        >
                          <LinkIcon className="h-4 w-4 mt-0.5 flex-shrink-0" />
                          <span className="line-clamp-2">{source.title}</span>
                        </a>
                        
                        {source.authors && (
                          <p className="text-xs text-gray-600 mb-1">
                            <span className="font-medium">Authors:</span> {source.authors}
                          </p>
                        )}
                        
                        {source.language && (
                          <p className="text-xs text-gray-600 mb-1">
                            <span className="font-medium">Language:</span> {source.language.toUpperCase()}
                          </p>
                        )}
                        
                        {source.topics && (
                          <div className="mt-2">
                            <p className="text-xs font-medium text-gray-700 mb-1">Topics:</p>
                            <p className="text-xs text-gray-600 line-clamp-2">{source.topics}</p>
                          </div>
                        )}
                        
                        {source.snippet && (
                          <p className="text-xs text-gray-600 mt-2 line-clamp-3 italic">
                            {source.snippet}
                          </p>
                        )}
                      </div>
                    ))
                ) : (
                  <div className="text-center text-gray-400 mt-12">
                    <Database className="h-10 w-10 mx-auto mb-3 opacity-50" />
                    <p className="text-sm">No sources yet</p>
                    <p className="text-xs mt-1">Ask a question to see source documents</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Ingest Tab */}
        {activeTab === 'ingest' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Ingest Articles</h2>

            {/* Ingest Type Toggle */}
            <div className="flex space-x-4 mb-6">
              <button
                onClick={() => setIngestType('search')}
                className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                  ingestType === 'search'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Search className="h-5 w-5 mr-2" />
                Search by Topic
              </button>
              <button
                onClick={() => setIngestType('url')}
                className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                  ingestType === 'url'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <LinkIcon className="h-5 w-5 mr-2" />
                Direct URL
              </button>
            </div>

            {/* Search Form */}
            {ingestType === 'search' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Topic *
                  </label>
                  <input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="e.g., artificial intelligence, climate change"
                    className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Website (optional)
                  </label>
                  <input
                    type="text"
                    value={website}
                    onChange={(e) => setWebsite(e.target.value)}
                    placeholder="e.g., bbc.com, nytimes.com"
                    className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Age (days)
                  </label>
                  <input
                    type="number"
                    value={maxAge}
                    onChange={(e) => setMaxAge(parseInt(e.target.value))}
                    min="1"
                    max="30"
                    className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>
              </div>
            )}

            {/* URL Form */}
            {ingestType === 'url' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Article URL *
                  </label>
                  <input
                    type="url"
                    value={articleUrl}
                    onChange={(e) => setArticleUrl(e.target.value)}
                    placeholder="https://example.com/article"
                    className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              onClick={handleIngest}
              disabled={ingestLoading || (ingestType === 'url' ? !articleUrl : !topic)}
              className="mt-6 w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {ingestLoading ? (
                <span className="flex items-center justify-center">
                  <Loader2 className="h-5 w-5 animate-spin mr-2" />
                  Processing...
                </span>
              ) : (
                'Ingest Article(s)'
              )}
            </button>

            {/* Result Message */}
            {ingestResult && (
              <div className={`mt-4 p-4 rounded-lg ${
                ingestResult.startsWith('✓') 
                  ? 'bg-green-50 text-green-800 border border-green-200'
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}>
                {ingestResult}
              </div>
            )}

            {/* Ingested Article Display */}
            {ingestedArticle && (
              <div className="mt-6 flex gap-4">
                {/* Main Article Content */}
                <div className="flex-1 bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    {ingestedArticle.article_title || 'Untitled'}
                  </h3>
                  
                  {ingestedArticle.article_url && (
                    <a 
                      href={ingestedArticle.article_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline text-sm mb-4 inline-block"
                    >
                      🔗 View Original Article
                    </a>
                  )}

                  <div className="prose max-w-none">
                    <h4 className="text-lg font-semibold text-gray-800 mt-4 mb-2">Article Text</h4>
                    <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                      {ingestedArticle.article_text || 'No content available'}
                    </p>
                  </div>
                </div>

                {/* Metadata Sidebar */}
                <div className="w-80 bg-white rounded-lg shadow-lg overflow-hidden flex flex-col border border-gray-200">
                  <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-3">
                    <h3 className="text-white font-semibold flex items-center">
                      <Database className="h-5 w-5 mr-2" />
                      Article Metadata
                    </h3>
                  </div>
                  
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {/* Summary */}
                    {ingestedArticle.article_summary && (
                      <div className="border-b border-gray-200 pb-3">
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">📝 Summary</h4>
                        <p className="text-sm text-gray-600 leading-relaxed">
                          {ingestedArticle.article_summary}
                        </p>
                      </div>
                    )}

                    {/* Authors */}
                    {ingestedArticle.article_authors && (
                      <div className="border-b border-gray-200 pb-3">
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">✍️ Authors</h4>
                        <p className="text-sm text-gray-600">
                          {ingestedArticle.article_authors}
                        </p>
                      </div>
                    )}

                    {/* Language */}
                    {ingestedArticle.article_language && (
                      <div className="border-b border-gray-200 pb-3">
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">🌐 Language</h4>
                        <p className="text-sm text-gray-600 uppercase">
                          {ingestedArticle.article_language}
                        </p>
                      </div>
                    )}

                    {/* Topics */}
                    {ingestedArticle.article_topics && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">🏷️ Topics</h4>
                        <p className="text-sm text-gray-600 leading-relaxed">
                          {ingestedArticle.article_topics}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
