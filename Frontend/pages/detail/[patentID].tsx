import { Image } from "@heroui/image";
import { Link } from "@heroui/link";
import { Button } from "@heroui/button";

import DefaultLayout from "@/layouts/default";

import { GetServerSideProps } from "next"
import { useRouter } from "next/router"
import { useState, useEffect } from "react";

import { IPatentInformation } from "@/types/detail/detail"

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
      <div className="max-w-4xl mx-auto bg-white shadow-md rounded-lg p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">侵權風險報告</h1>
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

      <div className="grid grid-cols-2 gap-4 mt-8">
        {/* 可能侵權內容 */}
        <div className="border p-4">
          <h2>LLM生成之可能侵權內容：</h2>
          <div className="h-20 border mt-2">
            asd
            asd
          </div>
        </div>

        {/* 相關專利節點圖 */}
        {/* react-graph-vis */}
        <div className="border p-4">
          <h2>相關專利節點圖：</h2>
          <Image
            src="/patent-network.png"
            alt="專利節點圖"
            width={200}
            height={200}
            className="mt-2"
          />
          <p className="text-xs text-gray-500">(最多20筆)</p>
        </div>
      </div>

      {/* 返回按鈕 */}
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
