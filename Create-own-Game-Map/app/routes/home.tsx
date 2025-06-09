import { useState, useEffect } from "react";
import type { Route } from "./+types/home";
import { useTranslation } from "react-i18next";
import i18next from "../i18n";
import { ClassNames } from "@emotion/react";

console.log(i18next.language);

export function meta({}: Route.MetaArgs) {
  return [
    { title: "New React Router App" },
    { name: "description", content: "Welcome to React Router!" },
  ];
}

const LanguageSwitcher = () => {
  const changeLanguage = (lng: string) => {
    i18next.changeLanguage(lng);
    localStorage.setItem("language", lng); // 🔹 Speichert die Sprache
  };

  return (
    <select
      onChange={(e) => changeLanguage(e.target.value)}
      value={i18next.language} // 🔹 Richtiges Attribut!
    >
      <option value="en">English</option>
      <option value="de">Deutsch</option>
      <option value="es">Español</option>
      <option value="ru">Русский</option>
    </select>
  );
};

export default function Home() {
  const [size, setSize] = useState(15);
  const values = [0, 1, 2]; // Mögliche Werte zum Umschalten
  const [grid, setGrid] = useState<number[][]>([]);
  const [mazeMode, setMazeMode] = useState(false);
  const { t } = useTranslation();

  // ⚡ `grid` aktualisieren, wenn sich `size` ändert
  useEffect(() => {
    const newGrid = Array.from({ length: size }, (_, rowIndex) =>
      Array.from({ length: size }, (_, colIndex) =>
        rowIndex === 0 ||
        rowIndex === size - 1 ||
        colIndex === 0 ||
        colIndex === size - 1
          ? -1 // Ränder bleiben -1
          : mazeMode && rowIndex % 2 === 0 && colIndex % 2 === 0
          ? -1 // Nur im Maze Mode werden diese Felder auf -1 gesetzt
          : 0
      )
    );
    setGrid(newGrid);
  }, [size, mazeMode]);

  // Schaltet den Wert eines Feldes zwischen 0 und 1 um, außer an den Rändern (diese bleiben immer 1)
  const toggleValue = (row: number, col: number) => {
    // Ränder dürfen nicht verändert werden
    if (row === 0 || row === size - 1 || col === 0 || col === size - 1) return;
    if (mazeMode && row % 2 === 0 && col % 2 === 0) return;
    setGrid((prevGrid) =>
      prevGrid.map((r, rowIndex) =>
        r.map(
          (value, colIndex) =>
            // Nur das angeklickte Feld wird geändert
            rowIndex === row && colIndex === col
              ? // Wert umschalten: 0 -> 1, 1 -> 0
                values[(values.indexOf(value) + 1) % values.length]
              : value // alle anderen Werte bleiben gleich
        )
      )
    );
  };

  const exportToPython = () => {
    const pythonCode = `game_map = [\n    ${grid
      .map((row) => `[${row.map((cell) => Math.abs(cell)).join(", ")}]`)
      .join(",\n    ")}\n]`;

    return pythonCode;
  };

  // in deiner React-Komponente
  const exportToPythonFile = () => {
    // 1. Python-Code zusammenbauen
    const pythonContent = exportToPython() ?? "";

    // 2. Blob erstellen
    const blob = new Blob([pythonContent], { type: "text/x-python" });
    const url = URL.createObjectURL(blob);

    // 3. Download-Link anlegen und klicken
    const a = document.createElement("a");
    a.href = url;
    a.download = "maze.py";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const setupMazePreset = () => {
    setGrid((prevGrid) =>
      prevGrid.map((row, rowIndex) =>
        row.map((value, colIndex) =>
          rowIndex === 0 ||
          rowIndex === size - 1 ||
          colIndex === 0 ||
          colIndex === size - 1
            ? -1
            : mazeMode && rowIndex % 2 === 0 && colIndex % 2 === 0
            ? -1
            : rowIndex % 2 === 0 || colIndex % 2 === 0
            ? 1
            : value
        )
      )
    );
  };

  return (
    <div className="h-screen">
      <div className="flex justify-between items-center p-4 bg-slate-300 border-1 border-slate-400/40 rounded-b-xl shadow-slate-400/60 shadow-lg sticky top-0">
        <div className="flex justify-start items-center gap-6">
          <h1 className="font-black text-center">
            <a href="https://github.com/Fren507">{t("title")}</a>
          </h1>
        </div>
        <div className="flex justify-end items-center gap-6">
          <div>
            <label htmlFor="size">{t("sizeLabel")}</label>
            <input
              type="number"
              name="size"
              id="size"
              min={5}
              max={25}
              value={size}
              step={2}
              onChange={(e) => setSize(Number(e.target.value))}
            />
          </div>
          <button
            className="px-4 py-2 bg-slate-400 rounded"
            onClick={() => setMazeMode(!mazeMode)}
          >
            {mazeMode ? t("mazeModeLabel") : t("normalModeLabel")}
          </button>
          <button
            onClick={setupMazePreset}
            className="px-4 py-2 bg-red-500 text-white rounded"
          >
            {t("mazePresetLabel")}
          </button>
          <div className="flex gap-1 drop-shadow shadow-slate-400/75">
            <button
              className="px-4 py-2 bg-slate-400 rounded-l"
              onClick={exportToPythonFile}
            >
              {t("exportLabel")}
            </button>
            <button
              className="px-4 py-2 bg-slate-400 rounded-r"
              onClick={() => console.log(exportToPython())}
            >
              {t("printLabel")}
            </button>
          </div>
          <div className="flex gap-6">
            <LanguageSwitcher />
          </div>
        </div>
      </div>
      <div className="flex justify-center items-center">
        <div
          className="grid gap-4 p-4"
          style={{
            gridTemplateColumns: `repeat(${size}, minmax(0, 1fr))`,
            maxHeight: `calc(100vh - 25px)`,
          }}
        >
          {grid.map((row, rowIndex) =>
            row.map((value, colIndex) => (
              <button
                onClick={() => toggleValue(rowIndex, colIndex)}
                key={`${rowIndex}-${colIndex}`}
                className={`${
                  value === 0
                    ? "bg-slate-300"
                    : value === 1
                    ? "bg-slate-600"
                    : value === -1
                    ? "bg-slate-900"
                    : value === 2
                    ? "bg-yellow-500"
                    : "bg-slate-950"
                } text-white rounded-lg p-4 text-center shadow-sm`}
                style={{ aspectRatio: "1/1" }}
              >
                {Math.abs(value)}
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
