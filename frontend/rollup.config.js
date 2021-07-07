import commonjs from "@rollup/plugin-commonjs";
import typescript from "@rollup/plugin-typescript";
import resolve from "@rollup/plugin-node-resolve";
import replace from "@rollup/plugin-replace";
import { terser } from "rollup-plugin-terser";

const production = process.env.NODE_ENV === "production";

export default {
  input: "src/index.ts",
  output: {
    file: "public/index.js",
    format: "iife",
    sourcemap: true,
  },
  plugins: [
    typescript(),
    resolve(),
    commonjs(),
    replace({
      "process.env.NODE_ENV": JSON.stringify(
        process.env.NODE_ENV || "development"
      ),
      preventAssignment: false,
    }),
    ...(production ? [terser()] : []),
  ],
};
