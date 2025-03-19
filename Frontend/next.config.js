/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      {
        source: "/detail",
        destination: "/detail/0",
        permanent: true,
      },
    ];
  },
};

module.exports = nextConfig
