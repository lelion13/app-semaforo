interface IdleScreenProps {
  empresaNombre: string;
  logoUrl: string;
  onStart: () => void;
}

export function IdleScreen({ empresaNombre, logoUrl, onStart }: IdleScreenProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-100 p-6">
      {logoUrl ? <img src={logoUrl} alt={empresaNombre} className="mb-4 max-h-32 w-auto object-contain" /> : null}
      <h1 className="mb-8 text-center text-3xl font-bold text-slate-800">{empresaNombre}</h1>
      <button
        className="rounded-2xl bg-blue-600 px-12 py-8 text-3xl font-bold text-white shadow-lg transition hover:bg-blue-700"
        onClick={onStart}
      >
        Iniciar control
      </button>
    </div>
  );
}
