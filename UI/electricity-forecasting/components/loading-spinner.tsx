"use client"

import { motion } from "framer-motion"

export function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] w-full">
      <div className="relative w-24 h-24">
        {/* Внешний круг */}
        <motion.div
          className="absolute inset-0 border-4 border-transparent border-t-primary border-r-primary rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 1.5, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
        />

        {/* Средний круг */}
        <motion.div
          className="absolute inset-2 border-4 border-transparent border-t-primary/70 border-l-primary/70 rounded-full"
          animate={{ rotate: -360 }}
          transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
        />

        {/* Внутренний круг */}
        <motion.div
          className="absolute inset-4 border-4 border-transparent border-b-primary/50 border-r-primary/50 rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 2.5, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
        />
      </div>

      <motion.div
        className="mt-6 text-lg font-medium text-primary"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.5 }}
      >
        Preparing your forecast...
      </motion.div>

      <motion.div
        className="mt-2 text-sm text-muted-foreground"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 0.5 }}
      >
        This may take a few moments
      </motion.div>
    </div>
  )
}
