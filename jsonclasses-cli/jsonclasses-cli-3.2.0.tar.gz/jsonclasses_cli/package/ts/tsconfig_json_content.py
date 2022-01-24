def tsconfig_json_content() -> str:
    return """
{
    "compilerOptions": {
        "baseUrl": ".",
        "outDir": "./lib",
        "declaration": true,
        "target": "es2016",
        "module": "commonjs",
        "jsx": "react",
        "lib": ["ESNext", "DOM"],
        "strict": true,
        "esModuleInterop": true,
        "skipLibCheck": true,
        "forceConsistentCasingInFileNames": true,
        "resolveJsonModule": true
    },
    "include": ["src", "index.ts"],
    "exclude": ["node_modules", "**/__tests__/*"]
}
    """.strip() + '\n'
