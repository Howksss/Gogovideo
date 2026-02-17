export const appStyles = `
  @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

  .v-app {
    --bg: #F2FFFE;
    --card: #FFFFFF;
    --primary: #00C9B7;
    --primary-dark: #00A89A;
    --primary-soft: rgba(0,201,183,0.08);
    --primary-hover: rgba(0,201,183,0.14);
    --primary-glow: rgba(0,201,183,0.3);
    --warm: #FF9F0A;
    --warm-soft: rgba(255,159,10,0.08);
    --text: #1A1A1A;
    --text-2: #7A7A85;
    --text-3: #B8B8C0;
    --border: #E0EAE9;
    --danger: #FF3B30;
    --danger-soft: rgba(255,59,48,0.08);
    --success: #34C759;
    --purple: #8B5CF6;
    --purple-soft: rgba(139,92,246,0.08);

    --shadow-sm: 0 1px 2px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.06);
    --shadow-md: 0 2px 8px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.04);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06);
    --shadow-primary: 0 4px 16px var(--primary-glow);

    --spring: cubic-bezier(0.34, 1.56, 0.64, 1);
    --smooth: cubic-bezier(0.25, 0.1, 0.25, 1);

    font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  @keyframes cardSpring {
    0% { opacity: 0; transform: translateY(20px) scale(0.97); }
    55% { opacity: 1; transform: translateY(-4px) scale(1.008); }
    75% { transform: translateY(1px) scale(0.999); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
  }
  .card-spring {
    animation: cardSpring 450ms var(--smooth) forwards;
    opacity: 0;
  }

  @keyframes menuPop {
    0% { opacity: 0; transform: scale(0.8) translateY(-6px); }
    65% { opacity: 1; transform: scale(1.04) translateY(1px); }
    100% { opacity: 1; transform: scale(1) translateY(0); }
  }
  .menu-pop {
    animation: menuPop 200ms var(--spring) forwards;
    transform-origin: top right;
  }

  @keyframes barSpring {
    0% { transform: scaleX(0); }
    65% { transform: scaleX(1.015); }
    100% { transform: scaleX(1); }
  }
  .bar-spring {
    transform-origin: left;
    animation: barSpring 900ms var(--smooth) forwards;
    animation-delay: 300ms;
    transform: scaleX(0);
  }

  @keyframes checkBounce {
    0% { transform: scale(0) rotate(-12deg); opacity: 0; }
    55% { transform: scale(1.2) rotate(3deg); }
    100% { transform: scale(1) rotate(0); opacity: 1; }
  }
  .check-bounce {
    animation: checkBounce 350ms var(--spring) forwards;
  }

  @keyframes floatUp {
    0% { opacity: 0; transform: translateY(20px); }
    100% { opacity: 1; transform: translateY(0); }
  }
  .float-up {
    animation: floatUp 500ms var(--smooth) forwards;
    animation-delay: 100ms;
    opacity: 0;
  }

  @keyframes breathe {
    0%, 100% { box-shadow: 0 4px 16px var(--primary-glow); }
    50% { box-shadow: 0 6px 28px rgba(0,201,183,0.4); }
  }
  .btn-breathe {
    animation: breathe 2.5s ease-in-out infinite;
  }

  @keyframes sheetUp {
    0% { transform: translateY(100%); }
    100% { transform: translateY(0); }
  }
  .sheet-up {
    animation: sheetUp 400ms var(--spring) forwards;
  }

  @keyframes overlayIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  .overlay-in {
    animation: overlayIn 200ms ease-out forwards;
  }

  .progress-ring {
    transform: rotate(-90deg);
    transform-origin: center;
  }
  .progress-ring circle {
    fill: none;
    stroke-linecap: round;
  }

  @keyframes headerSlide {
    from { opacity: 0; transform: translateY(-8px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .header-slide {
    animation: headerSlide 300ms var(--smooth) forwards;
  }

  .search-box {
    transition: border-color 200ms ease, box-shadow 200ms ease;
  }
  .search-box:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px var(--primary-soft), var(--shadow-sm) !important;
  }

  .grid-bg {
    background-color: var(--bg);
    background-image:
      linear-gradient(rgba(0,0,0,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,0,0,0.04) 1px, transparent 1px);
    background-size: 44px 44px;
    background-attachment: fixed;
  }

  .rename-input {
    transition: border-color 150ms ease, box-shadow 150ms ease;
  }
  .rename-input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px var(--primary-soft) !important;
    outline: none;
  }
`
