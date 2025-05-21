import { useState } from "react";
import { Button, addToast, Input, Image } from "@heroui/react";

import DefaultLayout from "@/layouts/default";

export default function LoginPage() {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const handleLogin = (event: React.FormEvent) => {
    event.preventDefault();
    console.log("Login attempt:", { username, password });

    if (username && password) {
      addToast({
        title: "Toast Title",
        description: "Toast Description",
      });
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
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className="text-left space-y-3">
              <label className="block font-medium mb-1">密碼：</label>
              <Input
                className="w-full"
                placeholder="輸入密碼"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
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
