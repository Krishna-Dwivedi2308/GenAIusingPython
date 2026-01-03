import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {z} from "zod";

const server=new McpServer({
  name:"test",
  version:"1.0.0",
  port:3000,
  
})

server.registerTool('addTwoNumbers',{
    title:'Add Two Numbers',
    description:'Add two numbers',
    inputSchema:{a:z.number(),b:z.number()},
},async function ({a,b}){
    // 
    return {content:[{type:'text',text:String(a+b)}]
    }
})
const transport = new StdioServerTransport();
await server.connect(transport);