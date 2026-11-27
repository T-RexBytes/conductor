# Stock reservations

- A reservation holds a positive whole number of units for one SKU. Creating
  one requires an existing SKU and enough available units.
- Available units equal on-hand units minus the quantities held by active
  reservations for that SKU. A hold counts only while the supplied time is
  earlier than its expiration timestamp.
- The store calculates expiration from the caller's time and TTL. Releasing
  a known ID deletes its record, even if its hold already expired.
- Removing an item still returns the item or None. It also removes that SKU's
  reservations so a replacement starts with its full on-hand quantity.
