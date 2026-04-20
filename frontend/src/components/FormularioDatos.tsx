import { useState } from "react";

interface FormularioDatosProps {
  onSubmit: (data: { legajo: string; nombre: string; apellido: string }) => Promise<void>;
}

export function FormularioDatos({ onSubmit }: FormularioDatosProps) {
  const [legajo, setLegajo] = useState("");
  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    if (!legajo.trim() || !nombre.trim() || !apellido.trim()) {
      setError("Completa todos los campos.");
      return;
    }
    if (!/^\d+$/.test(legajo.trim())) {
      setError("El legajo debe ser numerico.");
      return;
    }
    await onSubmit({ legajo: legajo.trim(), nombre: nombre.trim(), apellido: apellido.trim() });
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-xl rounded-2xl bg-white p-6 shadow-xl">
      <label className="mb-3 block">
        <span className="mb-1 block text-base font-semibold">Legajo</span>
        <input
          className="w-full rounded-lg border border-gray-300 px-4 py-3 text-lg"
          value={legajo}
          onChange={(e) => setLegajo(e.target.value)}
          inputMode="numeric"
          required
        />
      </label>
      <label className="mb-3 block">
        <span className="mb-1 block text-base font-semibold">Nombre</span>
        <input
          className="w-full rounded-lg border border-gray-300 px-4 py-3 text-lg"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          required
        />
      </label>
      <label className="mb-4 block">
        <span className="mb-1 block text-base font-semibold">Apellido</span>
        <input
          className="w-full rounded-lg border border-gray-300 px-4 py-3 text-lg"
          value={apellido}
          onChange={(e) => setApellido(e.target.value)}
          required
        />
      </label>
      {error ? <p className="mb-4 text-sm text-red-700">{error}</p> : null}
      <button className="w-full rounded-xl bg-red-700 px-4 py-4 text-xl font-bold text-white hover:bg-red-800">
        Confirmar y enviar
      </button>
    </form>
  );
}
