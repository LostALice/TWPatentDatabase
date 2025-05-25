import {
  Link,
  Table,
  TableHeader,
  TableBody,
  TableColumn,
  TableRow,
  TableCell,
  Spinner
} from "@heroui/react";
import { Button } from "@heroui/button";
import { GetServerSideProps } from "next"
import { useRouter } from "next/router"
import { useEffect, useState } from "react";
import ReactMarkdown from 'react-markdown';
import DefaultLayout from "@/layouts/default";
import { getPatentInfo, generateInfringementPatent, generatePatentGraph } from "@/api/patentId";
import { IPatentInfoModel } from "@/types/search";

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { resolvedUrl } = context
  const regex = /^\/result\/\d+$/

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
  const [patentInfo, setPatentInfo] = useState<IPatentInfoModel>()
  const [isGeneratingContent, setIsGeneratingContent] = useState(false)
  const [isGeneratingGraph, setIsGeneratingGraph] = useState(false)
  const [LLMContent, setLLMContent] = useState<string>("")
  const [GraphContent, setGraphContent] = useState<string>("")

  if (!patentID) {
    return (
      <DefaultLayout>
        <div className="text-center text-red-500">找不到該專利資訊</div>
      </DefaultLayout>
    )
  }

  useEffect(() => {
    const requestPatentInfo = async () => {
      const result = await getPatentInfo(patentID)
      console.log(result)
      setPatentInfo(result)
    }


    requestPatentInfo()
  }, [])

  const requestGenerateLLMContent = async () => {
    setIsGeneratingContent(true)
    const result = await generateInfringementPatent(patentID)
    console.log(result)
    setLLMContent(result)
    setIsGeneratingContent(false)
  }
  // requestGenerateLLMContent()

  const requestGenerateGraph = async () => {
    setIsGeneratingGraph(true)
    const result = await generatePatentGraph(patentID)
    console.log(result)
    setIsGeneratingGraph(false)
  }
  // requestGenerateGraph()

  if (!patentInfo) {
    return (
      <DefaultLayout>
        <div className="text-center text-red-500">找不到該專利資訊</div>
      </DefaultLayout>
    )
  }
  const patentLabel = [
    { label: "專利ID", item: "Patent_id" },
    { label: "標題", item: "Title" },
    { label: "申請日", item: "ApplicationDate" },
    { label: "公開日", item: "PublicationDate" },
    { label: "申請號", item: "ApplicationNumber" },
    { label: "公開號", item: "PublicationNumber" },
    { label: "申請人", item: "Applicant" },
    { label: "發明人", item: "Inventor" },
    { label: "代理人", item: "Attorney" },
    { label: "優先權", item: "Priority" },
    { label: "公報IPC", item: "GazetteIPC" },
    { label: "IPC", item: "IPC" },
    { label: "公報卷期", item: "GazetteVolume" },
    { label: "類別碼", item: "KindCodes" },
    { label: "URL", item: "PatentURL" },
  ]

  return (
    <DefaultLayout>
      <div className="mx-auto shadow-md rounded-lg p-8 m-8">
        <h1 className="text-3xl font-bold gap-5 p-1">侵權風險報告</h1>
        <div className="grid grid-cols-2 gap-4 mt-8 rounded-md mb-3">
          <div className="border p-4 rounded-md">
            <h2>LLM生成之可能侵權內容：</h2>
              {LLMContent ? <ReactMarkdown>{LLMContent}</ReactMarkdown> : <Button onPress={requestGenerateLLMContent}>LLM生成侵權內容</Button>}
          </div>

          <div className="border p-4 rounded-md">
            <h2>相關專利節點圖：</h2>
            {GraphContent ? <span>asd</span> : <Button onPress={requestGenerateGraph}>生成專利節點圖</Button>}

          </div>
        </div>
        <Table aria-label="Example static collection table" isStriped bottomContent={
          <Button
            className="mt-3"
            as={Link}
            href="/search"
          >
            返回
          </Button>
        }>
          <TableHeader >
            <TableColumn>項目</TableColumn>
            <TableColumn>內容</TableColumn>
          </TableHeader>
          <TableBody items={patentLabel} emptyContent={"找不到該專利資訊"}>
            {(item) => (
              <TableRow key={item.item}>
                <TableCell className="text-nowrap">{item.label}</TableCell>
                <TableCell>{patentInfo[item.item as keyof IPatentInfoModel]}</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </DefaultLayout>
  );
}
