import { Button, Link } from "@heroui/react";
import { getCookie } from "cookies-next";
import DefaultLayout from "@/layouts/default";
import { useEffect } from "react";
import { verifyLogin } from "@/api/index";
import { useState } from "react";

export default function IndexPage() {
  const access_token = getCookie("access_token");
  const refresh_token = getCookie("refresh_token");
  const [defaultLink, setDefaultLink] = useState<string>("/login");

  useEffect(() => {
    if (access_token && refresh_token) {
      const verify = async () => {
        const isLoggedIn = await verifyLogin()
        if (isLoggedIn) {
          setDefaultLink("/search")
        }
      }
      verify()
    }
  })

  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <div className="flex flex-col max-w-xl items-center text-center justify-center gap-3 space-y-5">
          <span className="text-4xl font-extrabold text-center my-8 tracking-tight">寶成專利智庫</span>
          <span className="text-xl text-center my-8 tracking-tight">一個收集專利資訊、分析專利的資料庫</span>
          <Button
            as={Link}
            className="px-8 py-3 rounded-md"
            href={defaultLink}
          >
            立即使用
          </Button>
        </div>
      </section>
    </DefaultLayout>
  );
}
