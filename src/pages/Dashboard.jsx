import { Bell, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import MetricCard from '../components/MetricCard';
import CircularScoreGauge from '../components/CircularScoreGauge';
import ProgressBar from '../components/ProgressBar';
import PrimaryButton from '../components/PrimaryButton';
import SecondaryButton from '../components/SecondaryButton';
import { Link } from 'react-router-dom';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } }
};

export default function Dashboard() {
  return (
    <div className="flex-1 flex flex-col p-[48px] pt-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-[48px] h-[64px]">
        <div>
          <h1 className="text-[28px] font-display font-bold text-text-primary">Good morning, Tahereem 👋</h1>
          <p className="text-[15px] text-text-secondary mt-1">Here's your study abroad overview</p>
        </div>
        <div className="flex items-center gap-4">
          <button className="w-[40px] h-[40px] rounded-full border border-border flex items-center justify-center text-text-secondary hover:text-text-primary hover:bg-white/5 transition-all">
            <Bell className="w-5 h-5" />
          </button>
          <PrimaryButton>Complete Profile</PrimaryButton>
        </div>
      </div>

      {/* Bento Grid */}
      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-3 gap-[16px] flex-1"
      >
        {/* Row 1 */}
        <motion.div variants={itemVariants} className="col-span-1">
          <MetricCard title="Loan Eligibility" accentClass="from-success to-primary" className="h-full flex flex-col items-center justify-center text-center">
            <CircularScoreGauge score={72} size={160} strokeWidth={8} label="Good standing" />
          </MetricCard>
        </motion.div>

        <motion.div variants={itemVariants} className="col-span-1">
          <MetricCard title="Expected ROI" accentClass="from-warning to-success" className="h-full">
            <div className="flex flex-col gap-4 mt-2">
              <div>
                <div className="text-[13px] text-text-secondary mb-1">Expected Salary</div>
                <div className="text-[32px] font-mono text-success leading-tight">$92,000<span className="text-[16px] text-text-tertiary">/yr</span></div>
              </div>
              <div className="h-[1px] w-full bg-border my-2"></div>
              <div>
                <div className="text-[13px] text-text-secondary mb-1">Total Cost</div>
                <div className="text-[24px] font-mono text-warning leading-tight">$45,000</div>
              </div>
            </div>
          </MetricCard>
        </motion.div>

        <motion.div variants={itemVariants} className="col-span-1">
          <MetricCard title="Interview Prep" accentClass="from-primary to-secondary" className="h-full flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-end mb-3 mt-4">
                <span className="text-[32px] font-mono text-text-primary leading-none">65%</span>
                <span className="text-[13px] text-text-secondary mb-1">3 topics remaining</span>
              </div>
              <ProgressBar progress={65} className="mb-6" />
            </div>
            <Link to="/visa-chat">
              <SecondaryButton className="w-full flex justify-center items-center gap-2">
                Continue Prep <ArrowRight className="w-4 h-4" />
              </SecondaryButton>
            </Link>
          </MetricCard>
        </motion.div>

        {/* Row 2 */}
        <motion.div variants={itemVariants} className="col-span-2">
          <MetricCard title="Career Insights" className="h-[300px]">
            <div className="flex h-full mt-4 flex-col gap-4">
              {/* Mock Bar Chart */}
              <div className="flex-1 flex flex-col justify-around">
                <div className="flex items-center gap-4">
                  <div className="w-32 text-[13px] text-text-secondary text-right">Data Scientist</div>
                  <div className="flex-1 h-[24px] bg-border rounded-r-sm overflow-hidden relative">
                    <motion.div initial={{width:0}} animate={{width:'85%'}} transition={{duration:1, delay:0.2}} className="h-full bg-gradient-to-r from-primary to-secondary"></motion.div>
                  </div>
                  <div className="w-20 text-[13px] font-mono text-text-primary">$115k</div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-32 text-[13px] text-text-secondary text-right">ML Engineer</div>
                  <div className="flex-1 h-[24px] bg-border rounded-r-sm overflow-hidden relative">
                    <motion.div initial={{width:0}} animate={{width:'95%'}} transition={{duration:1, delay:0.4}} className="h-full bg-gradient-to-r from-success to-primary"></motion.div>
                  </div>
                  <div className="w-20 text-[13px] font-mono text-text-primary">$130k</div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-32 text-[13px] text-text-secondary text-right">Software Dev</div>
                  <div className="flex-1 h-[24px] bg-border rounded-r-sm overflow-hidden relative">
                    <motion.div initial={{width:0}} animate={{width:'70%'}} transition={{duration:1, delay:0.6}} className="h-full bg-gradient-to-r from-primary to-secondary"></motion.div>
                  </div>
                  <div className="w-20 text-[13px] font-mono text-text-primary">$95k</div>
                </div>
              </div>
            </div>
          </MetricCard>
        </motion.div>

        <motion.div variants={itemVariants} className="col-span-1">
          <MetricCard title="Profile Snapshot" className="h-[300px] flex flex-col">
            <div className="flex-1 flex flex-col gap-4 mt-4">
              <div className="flex justify-between items-center border-b border-border pb-3">
                <span className="text-[13px] text-text-secondary">GPA</span>
                <span className="text-[15px] font-mono font-medium text-text-primary">3.8<span className="text-text-tertiary">/4.0</span></span>
              </div>
              <div className="flex justify-between items-center border-b border-border pb-3">
                <span className="text-[13px] text-text-secondary">Budget</span>
                <span className="text-[15px] font-mono font-medium text-text-primary">$50,000</span>
              </div>
              <div className="flex justify-between items-center border-b border-border pb-3">
                <span className="text-[13px] text-text-secondary">Target</span>
                <span className="text-[15px] font-medium text-text-primary">Germany 🇩🇪</span>
              </div>
            </div>
            <button className="text-[13px] text-primary hover:text-secondary transition-colors text-left mt-4 font-medium">
              Edit Profile →
            </button>
          </MetricCard>
        </motion.div>

        {/* Row 3 */}
        <motion.div variants={itemVariants} className="col-span-3">
          <div className="p-[20px] rounded-[16px] bg-surface border border-border shadow-card flex items-center justify-between card-hover">
            <div className="flex items-center gap-6 overflow-hidden flex-1">
              <span className="text-[12px] text-text-secondary uppercase tracking-[0.08em] font-medium shrink-0">Recent Activity</span>
              <div className="flex items-center gap-4 overflow-hidden flex-1">
                <div className="bg-elevated px-4 py-2 rounded-full text-[13px] text-text-primary whitespace-nowrap truncate border border-border">
                  <span className="text-text-tertiary mr-2">10:42 AM</span> How do I prove financial ties?
                </div>
                <div className="bg-primary/10 px-4 py-2 rounded-full text-[13px] text-primary whitespace-nowrap truncate border border-primary/20">
                  <span className="opacity-50 mr-2">10:43 AM</span> Show property deeds or business ownership...
                </div>
              </div>
            </div>
            <Link to="/visa-chat" className="text-[14px] text-primary hover:text-secondary font-medium whitespace-nowrap ml-6 flex items-center gap-1 transition-colors">
              Open Chat <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
