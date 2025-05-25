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
  Spinner,
  addToast,
  Tooltip,
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure
} from "@heroui/react";
import DefaultLayout from "@/layouts/default";
import { PatentTable } from "@/components/patentTable"
import { IPatentInfoModel } from "@/types/search"
import { fullTextSearch, similaritySearch, startScraper } from "@/api/search"

export default function SearchPage() {
  const [query, setQuery] = useState<string>("");
  const [searchMode, setSearchMode] = useState<boolean>(true)
  const [patentList, setPatentList] = useState<IPatentInfoModel[]>([])
  const [isSearching, setIsSearching] = useState<boolean>(false)
  const { isOpen, onOpen, onOpenChange } = useDisclosure();

  const handelSearch = () => {
    if (!query) {
      addToast({
        title: "搜尋鍵不能為空",
        color: "warning"
      })
      return
    }

    if (searchMode) {
      handleFullTextSearch()
    }
    else {
      handleSimilaritySearch()
    }
  }

  const handleFullTextSearch = async () => {
    setIsSearching(true)
    const results = await fullTextSearch(query);
    console.log(results)
    setPatentList(results)
    setIsSearching(false)
  };

  const handleSimilaritySearch = async () => {
    setIsSearching(true)
    const results = await similaritySearch(query);
    console.log(results)
    setQuery(results)
    setSearchMode(!searchMode)
    handleFullTextSearch()
    setIsSearching(false)
  }

  const handleStartScraping = async () => {
    if (!query) {
      addToast({
        title: "搜尋鍵不能為空",
        color: "warning"
      })
      return
    }
    console.log("Start Scraping")
    await startScraper(query)
    addToast({
      title: "已完成爬蟲",
      color: "success"
    })
  }

  return (
    <DefaultLayout>
      <Modal
        isDismissable={false}
        isKeyboardDismissDisabled={true}
        isOpen={isOpen}
        onOpenChange={onOpenChange}
      >
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">是否確認進行爬蟲?</ModalHeader>
              <ModalBody>
                <p>
                  即將開始執行爬蟲作業，預計耗時超過 30 分鐘。
                </p>
              </ModalBody>
              <ModalFooter>
                <Button color="danger" onPress={() => {
                  handleStartScraping()
                  onClose()
                }}>
                  確認
                </Button>
                <Button color="primary" onPress={onClose}>
                  取消
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
      <div className="flex flex-col items-center justify-center">
        <Card className="w-full h-full">
          <CardHeader className="flex gap-3 justify-between items-end">
            <Button
              as={Link}
              href="/history"
            >
              搜尋歷史
            </Button>
            <ButtonGroup>
              <Button onPress={() => { setSearchMode(!searchMode) }} >
                {searchMode ? "關鍵字" : "段落"}
              </Button>
              <Tooltip content="需時30分鐘以上" color="danger">
                <Button color="danger" onPress={onOpen}>開始爬蟲</Button>
              </Tooltip>
            </ButtonGroup>
          </CardHeader>
          <Divider />
          <CardBody>
            <div className="p-1 items-center flex space-x-2">
              <Input
                isClearable={true}
                className="w-full p-3 rounded-lg focus:ring-2"
                placeholder={searchMode ? "關鍵字搜尋" : "AI段落關鍵字搜尋"}
                type="text"
                value={query}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value)}
                onClear={() => setQuery("")}
              />
              <Button
                className="px-4 py-2 rounded-md"
                onPress={handelSearch}
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
              <Card className="w-full h-full my-3">
                <CardHeader className="flex gap-3 justify-center items-end">
                  {isSearching ?
                    <Spinner color="default" label="搜尋中" labelColor="foreground" /> :
                    <p>沒有有關專利</p>}
                </CardHeader>
              </Card>
            )
        }
      </div>
    </DefaultLayout >
  );
}
