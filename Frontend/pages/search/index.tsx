import { useState, useEffect, use } from "react";
import {
  Button,
  ButtonGroup,
  Image,
  Input,
  Link,
  Card,
  CardBody,
  CardHeader,
  CardFooter,
  Divider,
  Switch,
  addToast
} from "@heroui/react";
import { fullTextSearch } from "@/api/search"
import DefaultLayout from "@/layouts/default";
import { PatentTable } from "@/components/patentTable"
import { IPatentInfoModel } from "@/types/search"

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [isButtonEnable, setIsButtonEnable] = useState<boolean>(false);
  const [searchMode, setSearchMode] = useState<boolean>(true)
  const [patentList, setPatentList] = useState<IPatentInfoModel[]>([])

  const handleSearch = async () => {
    if (!query) {
      addToast({
        title: "搜尋鍵不能為空",
        color: "warning"
      })
      return
    }

    const results = await fullTextSearch(query);
    console.log(results)
    setPatentList(results)
  };

  return (
    <DefaultLayout>
      <div className="flex flex-col items-center justify-center">
        <Card className="w-full h-full">
          <CardHeader className="flex gap-3 justify-between items-end">
            <Button
              as={Link}
              href="/history"
            >
              搜尋歷史
            </Button>
            <div className="flex flex-row gap-2">
              <Button onPress={() => { setSearchMode(!searchMode) }} >
                {searchMode ? "關鍵字" : "段落"}
              </Button>
            </div>
          </CardHeader>
          <Divider />
          <CardBody>
            <div className="p-1 items-center flex space-x-2">
              <Input
                className="w-full p-3 rounded-lg focus:ring-2"
                placeholder={"搜尋專利之" + (searchMode ? "關鍵字" : "段落")}
                type="text"
                value={query}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value)}
              />
              <Button
                className="px-4 py-2 rounded-md"
                onPress={handleSearch}
              >
                搜尋
              </Button>
            </div>
          </CardBody>
          <Divider />
          <CardFooter>
            <Image
              alt="Pou Chen Group"
              src="https://www.pouchen.com/images/logo.png"
            />
          </CardFooter>
        </Card>
        {
          patentList.length > 0 ?
            (
              <>
                <PatentTable
                  patents={patentList}
                >
                </PatentTable>
              </>
            ) : (
              <>
                <Card className="w-full h-full my-3">
                  <CardHeader className="flex gap-3 justify-center items-end">
                    <p>沒有內容</p>
                  </CardHeader>
                </Card>
              </>
            )
        }
      </div>
    </DefaultLayout>
  );
}
