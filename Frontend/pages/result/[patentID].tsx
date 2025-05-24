import { Image } from "@heroui/image";
import { Link } from "@heroui/link";
import { Button } from "@heroui/button";
import { GetServerSideProps } from "next"
import { useRouter } from "next/router"
import { useState } from "react";

import DefaultLayout from "@/layouts/default";
import { IPatentInformation } from "@/types/detail"

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { resolvedUrl } = context
  const regex = /^\/detail\/\d+$/

  if (!regex.test(resolvedUrl)) {
    return { notFound: true }
  }

  return {
    props: {},
  }
}

export default function PatentDetail() {
  const router = useRouter()
  const patentID = Number(router.query.patentID) as number

  if (!patentID) {
    return (
      <DefaultLayout>
        <div className="text-center text-red-500">找不到該專利資訊</div>
      </DefaultLayout>
    )
  }

  const [patentInfo, setPatentInfo] = useState<IPatentInformation>(
    {
      id: "TW202505914B",
      name: "鞋履便捷穿脫設計",
      description: "改進的鞋類穿脫機制，提供更高便利性",
      applicant: "SKECHERS U.S.A.",
      location: "MANHATTAN BEACH, CALIFORNIA 90266, U.S.A. (US)",
      keyword: "便捷",
      risk: "中"
    },
  )


  // useEffect(() => {

  // }, [])

  return (
    <DefaultLayout>
      <div className="max-w-4xl mx-auto shadow-md rounded-lg p-8">
        <h1 className="text-3xl font-bold mb-6">侵權風險報告</h1>
        <div className="space-y-4">
          <div className="flex">
            <span className="w-32">公開公告號:</span>
            <span>{patentInfo.id}</span>
          </div>
          <div className="flex">
            <span className="w-32">專利名稱:</span>
            <span>{patentInfo.name}</span>
          </div>
          <div className="flex">
            <span className="w-32">申請人:</span>
            <span>{patentInfo.applicant}</span>
            <span>{patentInfo.location}</span>
          </div>
          <div className="flex">
            <span className="w-32">Risk:</span>
            <span>{patentInfo.risk}</span>
          </div>
          <div className="flex">
            <span className="w-32">相關專利:</span>
            <span>{patentInfo.keyword}</span>
          </div>
          <div className="flex">
            <span className="w-32">簡介:</span>
            <span>{patentInfo.description}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-8 rounded-md">
        <div className="border p-4 rounded-md">
          <h2>LLM生成之可能侵權內容：</h2>
        </div>

        <div className="border p-4 rounded-md">
          <h2>相關專利節點圖：</h2>
          {/* <Image
            alt="專利節點圖"
            className="mt-2"
            height={200}
            src="/patent-network.png"
            width={200}
          /> */}
        </div>
      </div>

      <div className="mt-6">
        <Button
          as={Link}
          href="/"
        >
          返回
        </Button>
      </div>
    </DefaultLayout>
  );
}
