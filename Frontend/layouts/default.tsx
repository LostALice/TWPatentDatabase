import { Head } from "./head";

import { Providers } from "@/components/providers";
import { Navbar } from "@/components/navbar";
import Transition from "@/components/transition/transition";

export default function DefaultLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <Providers>
      <div className="relative flex flex-col h-screen">
        <Head />
        <Navbar />
        <main className="container mx-auto max-w-7xl px-6 flex-grow">
          <Transition>{children}</Transition>
        </main>
      </div>
    </Providers>
  );
}
