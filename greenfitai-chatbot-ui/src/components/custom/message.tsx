import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cx } from 'classix';
import { BotIcon } from './icons';
import { Markdown } from './markdown';
import { MessageActions } from '@/components/custom/actions';
import EvaluationChart from '@/components/custom/chart'

interface Message {
  content: {
    text: string;
    chartData?: number[];
  };
  role: "user" | "assistant";
  id: string;
}

export const PreviewMessage = ({ message }: { message: Message }) => {
  const [showChart, setShowChart] = useState(false);

  useEffect(() => {
    // Show chart immediately if chart data exists
    setShowChart(message.content.chartData != null);
  }, [message.content]);

  return (
    <motion.div
      className="w-full mx-auto max-w-3xl px-4 group/message"
      initial={{ y: 5, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      data-role={message.role}
    >
      <div
        className={cx(
          'group-data-[role=user]/message:bg-green-700 dark:group-data-[role=user]/message:bg-muted group-data-[role=user]/message:text-white flex gap-4 group-data-[role=user]/message:px-3 w-full group-data-[role=user]/message:w-fit group-data-[role=user]/message:ml-auto group-data-[role=user]/message:max-w-2xl group-data-[role=user]/message:py-2 rounded-xl'
        )}
      >
        {message.role === 'assistant' && (
          <div className="size-8 flex items-center rounded-full justify-center ring-1 shrink-0 ring-border">
            <BotIcon />
          </div>
        )}

        <div className="flex flex-col w-full gap-4">
          <div className="flex flex-col gap-4 text-left">
            <Markdown>{message.content.text}</Markdown>
          </div>

          {showChart && message.content.chartData && (
            <motion.div
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="w-full"
            >
              <EvaluationChart data={message.content.chartData} />
            </motion.div>
          )}

          {message.role === 'assistant' && (
            <MessageActions message={message} />
          )}
        </div>
      </div>
    </motion.div>
  );
};

export const LoadingDots = () => (
  <span className="inline-flex items-center gap-1">
    {[0, 1, 2].map((dot) => (
      <motion.span
        key={dot}
        className="w-1 h-1 bg-primary rounded-full"
        initial={{ opacity: 0.2 }}
        animate={{ opacity: 1 }}
        transition={{
          duration: 0.5,
          repeat: Infinity,
          repeatType: "reverse",
          delay: dot * 0.2
        }}
      />
    ))}
  </span>
);

export const ThinkingMessage = () => {
  return (
    <div className="flex flex-row gap-4 px-4 w-full md:max-w-3xl mx-auto items-start">
      <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
        <motion.div
          className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full"
          animate={{ rotate: 360 }}
          transition={{
            duration: 1,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      </div>
      <div className="flex-1 space-y-2 overflow-hidden">
        <motion.div
          className="rounded-xl bg-muted p-4"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <p className="text-sm">
            GreenFit AI is evaluating your products 
            <LoadingDots />
          </p>
        </motion.div>
      </div>
    </div>
  );
};