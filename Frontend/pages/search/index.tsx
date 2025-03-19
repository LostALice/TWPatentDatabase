import { useState } from "react";
import { useRouter } from "next/navigation";
import DefaultLayout from "@/layouts/default";

import {
  Button,
  Image,
  Input,
  Link,
  Card,
  CardBody,
  CardHeader,
  CardFooter,
  Divider,
} from "@heroui/react"

import { PouChenLogoIcon } from "@/components/icon/logo"
export default function SearchPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");

  const handleSearch = () => {
    if (query.trim() !== "") {
      // router.push(`/results?query=${encodeURIComponent(query)}`);
    }
  };

  return (
    <DefaultLayout>
      <div className="flex flex-col items-center justify-center">
        <Card className="w-full h-full">
          <CardHeader className="flex gap-3 justify-end items-end">
            <Button
              as={Link}
              showAnchorIcon
              className="px-4 py-2 rounded-md"
              href="/results"
            >
              搜尋歷史
            </Button>
          </CardHeader>
          <Divider />
          <CardBody>
            <div className="p-1 items-center flex space-x-2">
              <Input
                type="text"
                className="w-full p-3 rounded-lg focus:ring-2"
                placeholder="欲搜尋專利之關鍵字或段落"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <Button
                className="px-6 py-3 rounded-lg"
                onPress={handleSearch}
              >
                搜尋
              </Button>
            </div>
          </CardBody>
          <Divider />
          <CardFooter>
            <Image
              src="https://www.pouchen.com/images/logo.png"
              alt="Pou Chen Group"
            />
          </CardFooter>
        </Card>
      </div>
    </DefaultLayout>
  );
}
