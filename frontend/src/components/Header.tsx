export default function Header() {
  return (
    <header
      className="header-slide sticky top-0 z-40 backdrop-blur-md px-5 py-3.5"
      style={{
        background: 'rgba(242,255,254,0.88)',
        borderBottom: '1px solid var(--border)',
      }}
    >
      <div className="flex items-center gap-3">
        <img
          src="/logo.jpg"
          alt="GoGoVideo"
          className="w-9 h-9 rounded-xl object-cover"
          style={{ boxShadow: 'var(--shadow-sm)' }}
        />
        <h1 className="text-lg font-bold leading-tight">gogovideo</h1>
      </div>
    </header>
  )
}
