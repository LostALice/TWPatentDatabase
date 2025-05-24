import { useState } from "react";
import { Button, addToast, Input, Image } from "@heroui/react";
import { userLogin } from "@/api/login";
import { setCookie } from "cookies-next";

import DefaultLayout from "@/layouts/default";
import { useRouter } from "next/router";

export default function LoginPage() {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const router = useRouter()

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    console.log("Login attempt:", { username, password });

    if (!username || !password) {
      addToast({
        title: "請輸入用戶名和密碼！",
        description: "請輸入用戶名和密碼！",
        color: "warning"
      });
    }

    const loginToken = await userLogin(username, password);
    if (loginToken != null) {
      setCookie("refresh_token", loginToken.refresh_token)
      setCookie("access_token", loginToken.access_token)
      addToast({
        title: "登入成功",
        description: "登入成功",
        color: "success"
      });
      router.push("/search")
    } else {
      addToast({
        title: "登入失敗",
        description: "登入失敗",
        color: "warning"
      });
    }
  };

  return (
    <DefaultLayout>
      <div className="flex items-center justify-center">
        <div className="p-10 rounded-3xl shadow w-1/2 text-center border">
          <div className="flex justify-center mb-6">
            <Image
              alt="Pou Chen Group"
              src="https://www.pouchen.com/images/logo.png"
            />
          </div>
          <h2 className="text-3xl font-extrabold mb-6">專利智庫</h2>
          <form className="space-y-6" onSubmit={handleLogin}>
            <div className="text-left">
              <label className="block font-medium mb-1">用戶名：</label>
              <Input
                className="w-full"
                placeholder="輸入用戶名"
                type="text"
                value={username}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)}
              />
            </div>
            <div className="text-left space-y-3">
              <label className="block font-medium mb-1">密碼：</label>
              <Input
                className="w-full"
                placeholder="輸入密碼"
                type="password"
                value={password}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
              />
            </div>
            <Button className="w-full transition shadow-md" type="submit">
              登入
            </Button>
          </form>
        </div>
      </div>
    </DefaultLayout>
  );
}
