export function ErrorCamara() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-6 text-center">
      <div className="mb-4 text-7xl">📷✖</div>
      <h1 className="mb-2 text-2xl font-bold text-gray-900">Camara no disponible</h1>
      <p className="max-w-xl text-lg text-gray-700">
        Permiso de camara requerido. Configura el acceso en el navegador y recarga la pagina.
      </p>
    </div>
  );
}
