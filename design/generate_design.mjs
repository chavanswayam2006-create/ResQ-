import { stitch } from "@google/stitch-sdk";
import fs from "node:fs/promises";

const BRIEF = `Dark emergency control-room dashboard. Background #0B1220, panels #121A2B, text #E6EDF7.
Accents: alert red #EF4444, amber #F59E0B, safe green #22C55E, info cyan #22D3EE.
Fonts: Inter for UI, JetBrains Mono for data. 12px rounded cards, thin borders, large readable numbers, left sidebar.`;

const SCREENS = {
  command_center: `Command Center: sidebar (logo ResQ-Grid; links Command Center, Incident Intake, Lab Hub). Main area: 8x8 city grid map with roads, blue flooded tiles, grey blocked tiles, hospital and fire-station icons, red/amber incident markers, unit icons. Right panel: Incident Queue with urgency bars sorted high to low. Bottom: AI Decision Log. Top bar buttons: Step, Auto-run, Reset.`,
  intake: `Incident Intake: report text area with 3 next-word suggestion chips below it, sector dropdown, sliders for hazard intensity and people at risk, a Dispatch button, and a result card with urgency gauge, chosen unit and route length.`,
  lab_hub: `Lab Hub: grid of 10 numbered cards 01-10, each with title, one-line description and an Open Lab button. Titles: PEAS Agent, Prolog Rule Brain, BFS/DFS Scout, A* Router and Puzzle, Minimax Strategy, Fuzzy Urgency, Mamdani vs Sugeno, Neuro-Fuzzy Predictor, Neural Learning Rules, Language Model Alerts.`,
  lab_detail: `Generic lab page: header with lab number and title, collapsible Aim and Theory box, left controls panel (inputs + Run button), right output area with a chart placeholder and a results table, bottom Viva Quick Facts list.`,
};

async function main() {
  const project = await stitch.createProject("ResQ-Grid");
  for (const [name, prompt] of Object.entries(SCREENS)) {
    try {
      const screen = await project.generate(`${BRIEF}\n\n${prompt}`, "DESKTOP");
      const htmlUrl = await screen.getHtml();
      const imgUrl = await screen.getImage();
      if (htmlUrl) {
        const html = await (await fetch(htmlUrl)).text();
        await fs.writeFile(`design/${name}.html`, html);
      }
      if (imgUrl) {
        const imgBuffer = Buffer.from(await (await fetch(imgUrl)).arrayBuffer());
        await fs.writeFile(`design/${name}.png`, imgBuffer);
      }
      console.log("saved", name);
    } catch (err) {
      console.error("Error generating", name, err);
    }
  }
}

if (process.argv[1]?.endsWith("generate_design.mjs")) {
  main().catch(console.error);
}
