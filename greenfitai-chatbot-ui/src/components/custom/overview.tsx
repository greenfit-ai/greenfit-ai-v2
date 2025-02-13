import { motion } from 'framer-motion';
import { Dumbbell, Sprout } from 'lucide-react';

export const Overview = () => {
  return (
    <>
    <motion.div
      key="overview"
      className="max-w-3xl mx-auto md:mt-20"
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ delay: 0.75 }}
    >
      <div className="rounded-xl p-6 flex flex-col gap-8 leading-relaxed text-center max-w-xl">
        <p className="flex flex-row justify-center gap-4 items-center">
          <Dumbbell size={44}/>
          <span>+</span>
          <Sprout size={44}/>
        </p>
        <p>
          Welcome to <strong className="text-green-500">GreenFit AI</strong>, where you can find out<br />
          about the <strong className="text-green-500">sustainability of your sports products</strong> in one click!<br />
          Visit us on our <strong><a href='https://greenfitai.org/' className="text-green-500 underline">website</a></strong> and read our <strong><a href='https://greenfitai.info/' className="text-green-500 underline">documentation</a></strong>.
        </p>
      </div>
    </motion.div>
    </>
  );
};
