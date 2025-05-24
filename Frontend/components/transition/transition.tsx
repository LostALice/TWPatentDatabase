"use client"

import { motion } from "framer-motion"

export default function Transition({
    children
}: {
    children: React.ReactNode
}) {
    return (
        <motion.div
            animate={{ y: 0, opacity: 1 }}
            initial={{ y: 20, opacity: 0 }}
            transition={{ ease: "easeInOut", duration: 0.4 }}
        >
            {children}
        </motion.div>
    )
}