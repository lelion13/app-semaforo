import { FormularioDatos } from "./FormularioDatos";

interface ResultadoRojoProps {
  onSubmit: (data: { legajo: string; nombre: string; apellido: string }) => Promise<void>;
}

export function ResultadoRojo({ onSubmit }: ResultadoRojoProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-red-600 p-6">
      <h2 className="mb-6 text-center text-4xl font-black text-white">Control requerido</h2>
      <FormularioDatos onSubmit={onSubmit} />
    </div>
  );
}
