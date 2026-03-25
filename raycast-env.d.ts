/// <reference types="@raycast/api">

/* 🚧 🚧 🚧
 * This file is auto-generated from the extension's manifest.
 * Do not modify manually. Instead, update the `package.json` file.
 * 🚧 🚧 🚧 */

/* eslint-disable @typescript-eslint/ban-types */

type ExtensionPreferences = {}

/** Preferences accessible in all the extension's commands */
declare type Preferences = ExtensionPreferences

declare namespace Preferences {
  /** Preferences accessible in the `search-show` command */
  export type SearchShow = ExtensionPreferences & {}
}

declare namespace Arguments {
  /** Arguments passed to the `search-show` command */
  export type SearchShow = {
  /** Show name or IMDb URL */
  "query": string,
  /** Min ratio (default: 0) */
  "minRatio": string
}
}

