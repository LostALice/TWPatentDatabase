import { useState, useEffect, use } from "react";
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
} from "@heroui/react";

import DefaultLayout from "@/layouts/default";

export default function SearchPage() {
  const [query, setQuery] = useState("");

  const handleSearch = () => {
    console.log(query);
  };

  return (
    <DefaultLayout>
      <div className="flex flex-col items-center justify-center">
        <Card className="w-full h-full">
          <CardHeader className="flex gap-3 justify-end items-end">
            <Button
              as={Link}
              className="px-4 py-2 rounded-md"
              href="/history"
            >
              搜尋歷史
            </Button>
          </CardHeader>
          <Divider />
          <CardBody>
            <div className="p-1 items-center flex space-x-2">
              <Input
                className="w-full p-3 rounded-lg focus:ring-2"
                placeholder="欲搜尋專利之關鍵字或段落"
                type="text"
                value={query}
                onChange={(e: Input.event) => setQuery(e.target.value)}
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
      </div>
    </DefaultLayout>
  );
}
