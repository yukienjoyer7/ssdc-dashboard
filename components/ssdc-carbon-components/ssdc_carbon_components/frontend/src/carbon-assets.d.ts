interface CarbonAssetNode {
  elem: string;
  attrs?: Record<string, string | number>;
  content?: CarbonAssetNode[];
}

declare module "@carbon/icons/es/dashboard/16.js" {
  const icon: CarbonAssetNode;
  export default icon;
}

declare module "@carbon/icons/es/task/16.js" {
  const icon: CarbonAssetNode;
  export default icon;
}

declare module "@carbon/icons/es/search/16.js" {
  const icon: CarbonAssetNode;
  export default icon;
}

declare module "@carbon/icons/es/warning--alt/16.js" {
  const icon: CarbonAssetNode;
  export default icon;
}

declare module "@carbon/icons/es/chart--line/16.js" {
  const icon: CarbonAssetNode;
  export default icon;
}
