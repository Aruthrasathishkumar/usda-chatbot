// RuralIllustration.jsx — Abstract rural landscape SVG
// Used in the welcome screen as a tasteful visual element

export default function RuralIllustration({ className = '' }) {
  return (
    <svg
      viewBox="0 0 480 200"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      role="img"
      aria-label="Abstract rural landscape illustration"
    >
      {/* Sky gradient */}
      <defs>
        <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#e0f2fe" />
          <stop offset="100%" stopColor="#f0fdf4" />
        </linearGradient>
        <linearGradient id="hillGrad1" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#86efac" stopOpacity="0.3" />
          <stop offset="100%" stopColor="#6ee7b7" stopOpacity="0.15" />
        </linearGradient>
        <linearGradient id="hillGrad2" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#34d399" stopOpacity="0.25" />
          <stop offset="100%" stopColor="#a7f3d0" stopOpacity="0.1" />
        </linearGradient>
        <linearGradient id="hillGrad3" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#059669" stopOpacity="0.2" />
          <stop offset="100%" stopColor="#6ee7b7" stopOpacity="0.08" />
        </linearGradient>
      </defs>

      {/* Background */}
      <rect width="480" height="200" fill="url(#skyGrad)" rx="12" />

      {/* Sun */}
      <circle cx="380" cy="45" r="24" fill="#fbbf24" fillOpacity="0.25" />
      <circle cx="380" cy="45" r="16" fill="#fbbf24" fillOpacity="0.15" />

      {/* Distant hills */}
      <path d="M0 140 Q60 100 120 120 Q180 90 240 115 Q320 85 400 110 Q440 95 480 108 L480 200 L0 200Z" fill="url(#hillGrad1)" />

      {/* Middle hills */}
      <path d="M0 160 Q80 125 160 145 Q220 120 300 140 Q380 115 480 135 L480 200 L0 200Z" fill="url(#hillGrad2)" />

      {/* Foreground hills */}
      <path d="M0 175 Q100 150 200 165 Q280 148 360 160 Q420 152 480 158 L480 200 L0 200Z" fill="url(#hillGrad3)" />

      {/* Simple barn silhouette */}
      <g transform="translate(140, 118)" opacity="0.35">
        <rect x="0" y="8" width="20" height="16" rx="1" fill="#334e68" />
        <polygon points="10,-2 -2,8 22,8" fill="#334e68" />
        <rect x="7" y="15" width="6" height="9" rx="0.5" fill="#243b53" />
      </g>

      {/* Simple house */}
      <g transform="translate(310, 125)" opacity="0.3">
        <rect x="0" y="6" width="16" height="12" rx="1" fill="#334e68" />
        <polygon points="8,-2 -2,6 18,6" fill="#334e68" />
        <rect x="5" y="11" width="5" height="7" rx="0.5" fill="#243b53" />
      </g>

      {/* Wind turbine */}
      <g transform="translate(90, 105)" opacity="0.2">
        <rect x="1" y="10" width="2" height="30" fill="#334e68" />
        <circle cx="2" cy="10" r="1.5" fill="#334e68" />
        <line x1="2" y1="10" x2="2" y2="-2" stroke="#334e68" strokeWidth="1" />
        <line x1="2" y1="10" x2="12" y2="16" stroke="#334e68" strokeWidth="1" />
        <line x1="2" y1="10" x2="-8" y2="16" stroke="#334e68" strokeWidth="1" />
      </g>

      {/* Communication tower (broadband) */}
      <g transform="translate(420, 100)" opacity="0.18">
        <polygon points="3,0 0,35 6,35" fill="#334e68" />
        <line x1="0" y1="12" x2="6" y2="12" stroke="#334e68" strokeWidth="0.8" />
        <line x1="0.5" y1="22" x2="5.5" y2="22" stroke="#334e68" strokeWidth="0.8" />
      </g>

      {/* Trees */}
      <g opacity="0.25">
        <ellipse cx="55" cy="150" rx="8" ry="12" fill="#059669" />
        <rect x="54" y="158" width="2" height="6" fill="#334e68" />
        <ellipse cx="250" cy="142" rx="6" ry="10" fill="#059669" />
        <rect x="249" y="148" width="2" height="5" fill="#334e68" />
        <ellipse cx="370" cy="148" rx="7" ry="11" fill="#059669" />
        <rect x="369" y="155" width="2" height="5" fill="#334e68" />
      </g>

      {/* Field lines (crop rows) */}
      <g opacity="0.1" stroke="#059669" strokeWidth="0.5">
        <line x1="160" y1="180" x2="320" y2="175" />
        <line x1="160" y1="184" x2="320" y2="179" />
        <line x1="160" y1="188" x2="320" y2="183" />
      </g>
    </svg>
  )
}
