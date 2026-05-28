/** Decorative mark: stacked document + scan beam (PDF metadata theme). */
export default function AppLogo() {
  return (
    <svg
      className="app-logo"
      viewBox="0 0 48 48"
      role="img"
      aria-hidden="true"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="logo-doc" x1="8" y1="6" x2="40" y2="42" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#60a5fa" />
          <stop offset="100%" stopColor="#2563eb" />
        </linearGradient>
        <linearGradient id="logo-scan" x1="4" y1="24" x2="44" y2="24" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#22d3ee" stopOpacity="0" />
          <stop offset="45%" stopColor="#38bdf8" stopOpacity="0.95" />
          <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
        </linearGradient>
        <filter id="logo-glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="1.2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <rect x="4" y="4" width="40" height="40" rx="12" fill="#1e293b" stroke="#334155" strokeWidth="1.5" />
      <path
        d="M14 10h14l8 8v24a2 2 0 0 1-2 2H14a2 2 0 0 1-2-2V12a2 2 0 0 1 2-2z"
        fill="url(#logo-doc)"
        filter="url(#logo-glow)"
      />
      <path d="M28 10v8h8" fill="#93c5fd" fillOpacity="0.35" stroke="#bfdbfe" strokeWidth="0.75" />
      <line x1="16" y1="22" x2="30" y2="22" stroke="#e2e8f0" strokeWidth="1.5" strokeLinecap="round" opacity="0.9" />
      <line x1="16" y1="27" x2="26" y2="27" stroke="#cbd5e1" strokeWidth="1.25" strokeLinecap="round" opacity="0.75" />
      <line x1="16" y1="32" x2="28" y2="32" stroke="#cbd5e1" strokeWidth="1.25" strokeLinecap="round" opacity="0.6" />
      <rect x="6" y="19" width="36" height="4" rx="2" fill="url(#logo-scan)" />
      <circle cx="36" cy="21" r="2.5" fill="#38bdf8" />
      <path
        d="M20 38l4-5 3 3 6-8 5 10"
        fill="none"
        stroke="#86efac"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
