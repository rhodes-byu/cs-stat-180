.tables
.schema Artist

-- -- Retrieve all artists in the database.
-- SELECT * FROM Artist;


-- -- Retreive all albums in the database.
-- SELECT * FROM Album;


-- Retrieve all tracks in the database.
-- SELECT * FROM Track;


-- -- Retrieve all playlists in the database.
-- SELECT * FROM Playlist;


-- -- List all albums by a specific artist (e.g., 'Audioslave').
-- SELECT al.AlbumId, al.Title 
-- FROM Album AS al
-- JOIN Artist AS ar ON al.ArtistId = ar.ArtistId
-- WHERE ar.Name = 'Audioslave';


-- -- Retrieve all tracks from a specific album (e.g., 'Restless and Wild').
-- SELECT t.TrackId AS TrackId, t.Name AS Name
-- FROM Track AS t
-- JOIN Album AS a ON t.AlbumId = a.AlbumId
-- WHERE a.Title = 'Restless and Wild';


-- -- List all albums along with their artist names.
-- SELECT al.Title AS Album, ar.Name AS Artist
-- FROM Album AS al
-- JOIN Artist AS ar ON al.ArtistId = ar.ArtistId
-- ORDER BY ar.Name, al.Title;


-- -- Find the total number of albums per artist.
-- SELECT ar.Name AS Name, COUNT(al.AlbumId) AS AlbumCount
-- FROM Artist AS ar
-- JOIN Album AS al ON ar.ArtistId = al.ArtistId
-- GROUP BY ar.Name
-- ORDER BY AlbumCount DESC;


-- -- Find all playlists and their total number of tracks.
-- SELECT p.PlaylistId AS PlaylistId, p.Name AS Name, COUNT(pt.TrackId) AS TrackCount
-- FROM Playlist AS p
-- LEFT JOIN PlaylistTrack AS pt ON p.PlaylistId = pt.PlaylistId
-- GROUP BY p.PlaylistId, p.Name;


-- -- Get the most popular playlists based on the number of tracks.
-- SELECT p.Name AS Name, COUNT(pt.TrackId) AS TrackCount
-- FROM Playlist AS p
-- JOIN PlaylistTrack AS pt ON p.PlaylistId = pt.PlaylistId
-- GROUP BY p.Name
-- ORDER BY TrackCount DESC;


-- -- Find tracks that appear in multiple playlists.
-- SELECT t.Name AS Name, COUNT(pt.PlaylistId) AS PlaylistCount
-- FROM Track AS t
-- JOIN PlaylistTrack AS pt ON t.TrackId = pt.TrackId
-- GROUP BY t.Name
-- HAVING COUNT(pt.PlaylistId) > 1
-- ORDER BY PlaylistCount DESC;


-- -- Find artists who have more than 3 albums.
-- SELECT ar.Name AS Name, COUNT(al.AlbumId) AS AlbumCount
-- FROM Artist AS ar
-- JOIN Album AS al ON ar.ArtistId = al.ArtistId
-- GROUP BY ar.Name
-- HAVING COUNT(al.AlbumId) > 3;


-- -- Find the top 5 longest tracks in the database.
-- SELECT Name AS Name, Milliseconds/60000 AS LengthInMinutes
-- FROM Track
-- ORDER BY Milliseconds DESC
-- LIMIT 5;


-- -- List the top 3 playlists with the highest number of tracks.
-- SELECT p.Name AS Name, COUNT(pt.TrackId) AS TrackCount
-- FROM Playlist AS p
-- JOIN PlaylistTrack AS pt ON p.PlaylistId = pt.PlaylistId
-- GROUP BY p.Name
-- ORDER BY TrackCount DESC
-- LIMIT 3;


-- -- Find all tracks that belong to an album with a specific artist (e.g., 'Queen').
-- SELECT t.Name AS Name, a.Title AS Album, ar.Name AS Artist
-- FROM Track AS t
-- JOIN Album AS a ON t.AlbumId = a.AlbumId
-- JOIN Artist AS ar ON a.ArtistId = ar.ArtistId
-- WHERE ar.Name = 'Queen';


-- -- Find all albums that contain at least one track appearing in more than one playlist.
-- SELECT DISTINCT al.Title AS Album, ar.Name AS Artist
-- FROM Album AS al
-- JOIN Track AS t ON al.AlbumId = t.AlbumId
-- JOIN PlaylistTrack AS pt ON t.TrackId = pt.TrackId
-- GROUP BY al.Title, ar.Name
-- HAVING COUNT(pt.PlaylistId) > 1;


-- -- Retrieve the artist with the most albums.
-- SELECT ar.Name AS Name, COUNT(al.AlbumId) AS AlbumCount
-- FROM Artist AS ar
-- JOIN Album AS al ON ar.ArtistId = al.ArtistId
-- GROUP BY ar.Name
-- ORDER BY AlbumCount DESC
-- LIMIT 1;

