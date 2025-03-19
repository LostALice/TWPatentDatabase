import { useState } from "react";
import { useRouter } from "next/navigation";
import { Image } from "@heroui/react";
import DefaultLayout from "@/layouts/default";

import { Button } from "@heroui/button"
import { Input } from "@heroui/input"

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const handleLogin = (event: React.FormEvent) => {
    event.preventDefault(); // 防止表單刷新
    console.log("Login attempt:", { username, password });

    // 簡單檢查是否有輸入，然後跳轉
    if (username && password) {
      router.push("/search");
    } else {
      alert("請輸入用戶名和密碼！");
    }
  };

  return (
    <DefaultLayout>
      <div className="flex items-center justify-center">
        <div className="p-10 rounded-3xl shadow w-1/2 text-center border">
          <div className="flex justify-center mb-6">
            <Image
              src="https://www.pouchen.com/images/logo.png"
              alt="Pou Chen Group"
            />
          </div>
          <h2 className="text-3xl font-extrabold mb-6">專利智庫</h2>
          <form onSubmit={handleLogin} className="space-y-6">
            <div className="text-left">
              <label className="block  font-medium mb-1">用戶名：</label>
              <Input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full"
                placeholder="輸入用戶名"
              />
            </div>
            <div className="text-left space-y-3">
              <label className="block font-medium mb-1">密碼：</label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full"
                placeholder="輸入密碼"
              />
            </div>
            <Button
              type="submit"
              className="w-full transition shadow-md"
            >
              登入
            </Button>
          </form>
        </div>
      </div>
    </DefaultLayout>
  );
}
