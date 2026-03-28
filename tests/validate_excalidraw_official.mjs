import fs from "node:fs";
import path from "node:path";

const fixturePath = path.resolve(
  "fixtures/target-repo-basic/docs/architecture/system-context.excalidraw",
);

async function main() {
  const raw = fs.readFileSync(fixturePath, "utf8");
  const payload = JSON.parse(raw);

  let restore;
  try {
    ({ restore } = await import("@excalidraw/excalidraw"));
  } catch (error) {
    console.log(
      JSON.stringify(
        {
          status: "environment_error",
          accepted: false,
          message:
            "Official Excalidraw runtime could not be loaded in this Node environment.",
          error: String(error),
        },
        null,
        2,
      ),
    );
    process.exitCode = 2;
    return;
  }

  const restored = restore(payload, {}, null, {
    refreshDimensions: false,
    repairBindings: true,
  });

  const result = {
    status: "accepted",
    accepted: Boolean(restored && Array.isArray(restored.elements)),
    elementCount: restored?.elements?.length ?? 0,
    appStatePresent: Boolean(restored?.appState),
    filesPresent: typeof restored?.files === "object" && restored?.files !== null,
  };

  console.log(JSON.stringify(result, null, 2));

  if (!result.accepted) {
    process.exitCode = 1;
  }
}

await main();
