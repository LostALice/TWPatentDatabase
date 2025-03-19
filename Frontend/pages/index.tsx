import { title, subtitle } from "@/components/primitives";
import DefaultLayout from "@/layouts/default";

import { Button, Link } from "@heroui/react";

export default function IndexPage() {
  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <div className="flex flex-col max-w-xl items-center text-center justify-center gap-3 space-y-5">
          <span className="text-4xl font-extrabold text-center my-8 tracking-tight">寶成專利智庫</span>
          <span className="text-xl text-center my-8 tracking-tight">一個收集專利資訊、分析專利的資料庫</span>
          <Button
            as={Link}
            className="px-8 py-3 rounded-md"
            href="/login"
          >
            立即使用
          </Button>
        </div>
      </section>
    </DefaultLayout>
  );
}
