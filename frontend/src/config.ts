const params = new URLSearchParams(location.search);
const env = params.get("env");
const chessvision = params.get("chessvision");

const config = {
  env,
  chessvision,
  baseUrl:
    env == "dev"
      ? `http://${location.hostname}:5000`
      : "https://web-vrnocjtpaa-an.a.run.app",
  resizeTarget: 1000,
};

export default config;
