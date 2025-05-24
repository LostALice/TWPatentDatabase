export type SiteConfig = typeof siteConfig;

export const siteConfig = {
  name: "寶成專利智庫",
  description: "寶成專利智庫",
  navItems: [
    {
      label: "搜尋",
      href: "/search",
    },
    {
      label: "歷史紀錄",
      href: "/history",
    },
  ],
  links: {
    github: "https://github.com/heroui-inc/heroui",
    twitter: "https://twitter.com/hero_ui",
    docs: "https://heroui.com",
    discord: "https://discord.gg/9b6yyZKmH4",
    sponsor: "https://patreon.com/jrgarciadev",
  },
  baseURL: "http://localhost:8000/api/v1",
};
