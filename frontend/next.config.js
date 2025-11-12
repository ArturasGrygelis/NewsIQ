/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        // Always use backend service name in Docker network
        destination: 'http://backend:8000/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig
